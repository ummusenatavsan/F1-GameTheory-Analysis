import fastf1
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os


if not os.path.exists('cache'):
    os.makedirs('cache')

fastf1.Cache.enable_cache('cache')


class GameTheoryF1:
    def __init__(self, year, gp, session_type='R'):
        print(f"\nVeriler indiriliyor: {year} {gp}...")
        self.session = fastf1.get_session(year, gp, session_type)
        self.session.load()
        self.laps = self.session.laps
        self.laps['LapTimeSeconds'] = self.laps['LapTime'].dt.total_seconds()
        print("Veri işleme tamamlandı.")

    #pit yolunda kaybettiğimiz süreyi hesaplıyoruz.
    def calculate_pit_loss(self):



        pit_laps = self.laps[~self.laps['PitOutTime'].isna()]
        clean_laps = self.laps.pick_quicklaps()
        avg_clean_lap = clean_laps['LapTimeSeconds'].median()
        avg_pit_lap = pit_laps['LapTimeSeconds'].median()

        #veri hatası varsa standart pit süresi olan 22 saniyeyi varsayıyoruz.
        if np.isnan(avg_pit_lap) or np.isnan(avg_clean_lap):
            return 22.0
        #sonucu fiziksel olarak mantıklı bir aralığa sabitliyoruz
        pit_loss = avg_pit_lap - avg_clean_lap
        return max(18.0, min(pit_loss, 28.0))

    #lastik farklarını hesaba katıyoruz.
    #Hamilton-Eski Hard / Verstappen Yeni Soft lastiklerde
    def calculate_pace_delta(self):

        return 3.5  # Saniye/Tur (Lastik Performans Farkı)
    #Safety Car etkisiyle pit kaybı
    def generate_payoff_matrix(self, gap_between_drivers, sc_probability=0.0):
        normal_pit_loss = self.calculate_pit_loss()
        sc_pit_loss = normal_pit_loss * 0.55  # SC altında pit %45 daha ucuz

        #Normal yarış ve SC senaryolarının olasılık ağırlıklı ortalamasıdır.
        #Belirsizlik altında karar vermek için SC ihtimalini hesaba katıyoruz.
        expected_pit_loss = (normal_pit_loss * (1 - sc_probability)) + (sc_pit_loss * sc_probability)

        #Lastik Performans Farkı
        tyre_pace_advantage = self.calculate_pace_delta()

        print(f"\n--- 2021 ABU DHABI FINAL SENARYOSU ---")
        print(f"Safety Car Olasılığı: %{sc_probability * 100}")
        print(f"Mevcut Fark: {gap_between_drivers} sn")
        print(f"Lastik Durumu: HAM (40 Tur Hard) vs VER (0 Tur Soft)")
        print(f"Hız Avantajı: Yeni Soft lastikler tur başına {tyre_pace_advantage} sn daha hızlı!")
        print(f"Beklenen Pit Maliyeti: {expected_pit_loss:.2f} sn (SC etkisiyle düştü)")

        #MATRİS HESAPLAMASI

        # Kalan tur sayısı (yarışın son kritik kısmını analizlediğimiz için tur sayısı az)
        laps_remaining = 2

        # A: STAY (Old Hard), B: STAY (Old Hard) -> Fark korunur, hatta A önde kalır.
        outcome_stay_stay = gap_between_drivers

        # A: STAY (Old Hard), B: PIT (New Soft) -> KRİTİK SENARYO
        # B pite girer (Pit Loss kadar kaybeder).
        # Ama kalan turlarda "Pace Advantage" kadar her tur geri kazanır.
        # Formül: Mevcut Fark - Pit Kaybı + (Hız Farkı * Kalan Tur)
        outcome_stay_pit = gap_between_drivers - expected_pit_loss + (tyre_pace_advantage * laps_remaining)

        # A: PIT, B: STAY -> A yeni lastik alır ama pist pozisyonunu kaybeder (Track Position).
        # Mercedes bunu yapmadı çünkü "Track Position is King" dediler.
        outcome_pit_stay = gap_between_drivers + expected_pit_loss - (tyre_pace_advantage * laps_remaining)

        # A: PIT, B: PIT -> İkisi de girerse fark değişmez
        outcome_pit_pit = gap_between_drivers

        matrix = [
            [outcome_stay_stay, outcome_stay_pit],
            [outcome_pit_stay, outcome_pit_pit]
        ]

        return matrix

    def visualize_nash(self, matrix, driver_leader, driver_follower):
        col_labels = [f"{driver_follower}: STAY\n(Old Hard)", f"{driver_follower}: PIT\n(New Soft)"]
        row_labels = [f"{driver_leader}: STAY\n(Old Hard)", f"{driver_leader}: PIT\n(New Soft)"]

        df = pd.DataFrame(matrix, columns=col_labels, index=row_labels)

        plt.figure(figsize=(12, 9))

        sns.heatmap(df, annot=True, fmt=".2f", cmap="RdYlGn",
                    linewidths=2, linecolor='black',
                    annot_kws={"size": 14, "weight": "bold"},
                    cbar_kws={'label': 'Yarış Sonu Tahmini Fark (Saniye)'})

        plt.title(f"2021 Abu Dhabi - Oyun Teorisi & Lastik Analizi\n{driver_leader} vs {driver_follower}", fontsize=16,
                  fontweight='bold', pad=20)
        plt.xlabel(f"{driver_follower} Kararı", fontsize=13, fontweight='bold')
        plt.ylabel(f"{driver_leader} Kararı", fontsize=13, fontweight='bold')

        plt.figtext(0.5, 0.02,
                    "Negatif değerler: Verstappen kazanır. Pozitif değerler: Hamilton kazanır.\nSenaryo: Safety Car Olasılığı ve New Soft vs Old Hard lastik farkı hesaba katılmıştır.",
                    ha="center", fontsize=11, bbox={"facecolor": "gold", "alpha": 0.2, "pad": 10})

        plt.tight_layout(pad=4.0)
        plt.show()


# --- ÇALIŞTIRMA KISMI ---
if __name__ == "__main__":
    game = GameTheoryF1(2021, 'Abu Dhabi')

    # SENARYO:
    # Latifi kazası sonrası. Hamilton önde ama lastikleri bitik.
    # Fark 11 saniye civarıydı ama SC çıkınca fark kapandı.
    # Biz karar anındaki (SC karar verilmeden hemen önceki) matematiğe bakıyoruz.

    current_gap = 10.0  # Aradaki fark
    safety_car_prob = 0.50  # %50 SC İhtimali (Çok yüksek risk)

    payoff_matrix = game.generate_payoff_matrix(current_gap, safety_car_prob)
    game.visualize_nash(payoff_matrix, driver_leader="HAMILTON", driver_follower="VERSTAPPEN")