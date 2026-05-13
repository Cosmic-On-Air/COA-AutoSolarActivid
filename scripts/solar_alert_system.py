"""
Solar Activity Alert System
Detects abnormal solar activities.

Alert thresholds based on NOAA standards:
- S1 (Minor): >=10 MeV flux > 10 pfu
- S2 (Moderate): >=10 MeV flux > 100 pfu
- S3 (Strong): >=10 MeV flux > 1000 pfu
- S4 (Severe): >=10 MeV flux > 10000 pfu
- S5 (Extreme): >=10 MeV flux > 100000 pfu
"""

import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
import requests

# Alert configuration (in protons·cm⁻²·s⁻¹·sr⁻¹)
ALERT_THRESHOLDS = {
    "S1_MINOR": 10,
    "S2_MODERATE": 100,
    "S3_STRONG": 1000,
    "S4_SEVERE": 10000,
    "S5_EXTREME": 100000
}

ALERT_LEVELS = {
    "S1_MINOR": {
        "name": "S1 - Minor",
        "color": "#FFD700",
        "description": "Minor biological risk for astronauts in EVA"
    },
    "S2_MODERATE": {
        "name": "S2 - Moderate",
        "color": "#FFA500",
        "description": "Increased radiation risk for high-altitude aircraft passengers"
    },
    "S3_STRONG": {
        "name": "S3 - Strong",
        "color": "#FF8C00",
        "description": "Possible HF radio disturbances in polar regions"
    },
    "S4_SEVERE": {
        "name": "S4 - Severe",
        "color": "#FF4500",
        "description": "Significant risks for polar flights and satellites"
    },
    "S5_EXTREME": {
        "name": "S5 - Extreme",
        "color": "#FF0000",
        "description": "⚠️ EMERGENCY LEVEL"
    }
}

# Base paths
ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "alert_config.json"
ALERT_LOG_FILE = ROOT / "alert_log.json"


class SolarAlertSystem:
    """Alert system for abnormal solar activities."""
    
    def __init__(self):
        self.config = self.load_config()
        self.alert_history = self.load_alert_history()
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                "alert_cooldown_hours": 6,
                "min_alert_level": "S2_MODERATE",
                "monitor_energies": [10, 50, 100]
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Dict):
        """Save configuration."""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def load_alert_history(self) -> List[Dict]:
        """Charge l'historique des alertes."""
        if ALERT_LOG_FILE.exists():
            with open(ALERT_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_alert_history(self):
        """Sauvegarde l'historique des alertes."""
        with open(ALERT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.alert_history, f, indent=2)
    
    def fetch_current_proton_data(self) -> Optional[List[Dict]]:
        """Récupère les données actuelles de flux de protons depuis NOAA."""
        try:
            url = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-6-hour.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des données: {e}")
            return None
    
    def analyze_data(self, data: List[Dict]) -> Dict[str, any]:
        """Analyse les données pour détecter les anomalies."""
        if not data:
            return {"alert": False}
        
        # Filtrer les énergies à surveiller
        monitor_energies = self.config.get("monitor_energies", [10, 50, 100])
        
        max_flux_by_energy = {}
        latest_readings = {}
        
        for entry in data:
            try:
                energy_str = entry.get("energy", "")
                if ">=" not in energy_str:
                    continue
                
                energy = float(energy_str.split(">=")[1].split()[0])
                
                if energy not in monitor_energies:
                    continue
                
                flux = float(entry.get("flux", 0))
                time_tag = entry.get("time_tag", "")
                
                if energy not in max_flux_by_energy or flux > max_flux_by_energy[energy]["flux"]:
                    max_flux_by_energy[energy] = {
                        "flux": flux,
                        "time": time_tag
                    }
                
                # Garder la lecture la plus récente
                if energy not in latest_readings or time_tag > latest_readings[energy]["time"]:
                    latest_readings[energy] = {
                        "flux": flux,
                        "time": time_tag
                    }
            except (ValueError, KeyError):
                continue
        
        # Déterminer le niveau d'alerte le plus élevé
        highest_alert = None
        alert_details = []
        
        for energy, reading in max_flux_by_energy.items():
            flux = reading["flux"]
            
            for threshold_key in reversed(list(ALERT_THRESHOLDS.keys())):
                threshold_value = ALERT_THRESHOLDS[threshold_key]
                
                if flux >= threshold_value:
                    alert_info = ALERT_LEVELS[threshold_key].copy()
                    alert_info["threshold_key"] = threshold_key
                    alert_info["energy"] = energy
                    alert_info["flux"] = flux
                    alert_info["time"] = reading["time"]
                    
                    alert_details.append(alert_info)
                    
                    if highest_alert is None or threshold_value > ALERT_THRESHOLDS[highest_alert]:
                        highest_alert = threshold_key
                    
                    break
        
        if highest_alert:
            return {
                "alert": True,
                "level": highest_alert,
                "level_name": ALERT_LEVELS[highest_alert]["name"],
                "details": alert_details,
                "latest_readings": latest_readings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "alert": False,
            "latest_readings": latest_readings,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def should_send_alert(self, alert_level: str) -> bool:
        """Vérifie si une alerte doit être envoyée (cooldown)."""
        min_level = self.config.get("min_alert_level", "S2_MODERATE")
        min_threshold = ALERT_THRESHOLDS.get(min_level, 100)
        current_threshold = ALERT_THRESHOLDS.get(alert_level, 0)
        
        # Ne pas alerter si le niveau est trop faible
        if current_threshold < min_threshold:
            return False
        
        # Vérifier le cooldown
        cooldown_hours = self.config.get("alert_cooldown_hours", 6)
        
        for past_alert in reversed(self.alert_history):
            if past_alert.get("level") == alert_level:
                past_time = datetime.fromisoformat(past_alert.get("timestamp"))
                now = datetime.now(timezone.utc)
                hours_diff = (now - past_time).total_seconds() / 3600
                
                if hours_diff < cooldown_hours:
                    print(f"⏳ Cooldown actif: {hours_diff:.1f}h / {cooldown_hours}h")
                    return False
                break
        
        return True
    
    def log_alert(self, analysis: Dict):
        """Enregistre l'alerte dans l'historique."""
        log_entry = {
            "timestamp": analysis["timestamp"],
            "level": analysis["level"],
            "level_name": analysis["level_name"],
            "details": analysis["details"],
            "latest_readings": analysis["latest_readings"]
        }
        self.alert_history.append(log_entry)
        self.save_alert_history()
        print(f"📝 Alerte enregistrée dans l'historique")
    
    def check_and_alert(self) -> Dict:
        """Vérifie les données et envoie des alertes si nécessaire."""
        print("🔍 Vérification de l'activité solaire...")
        
        # Récupérer les données actuelles
        data = self.fetch_current_proton_data()
        
        if not data:
            return {"status": "error", "message": "Impossible de récupérer les données"}
        
        # Analyser les données
        analysis = self.analyze_data(data)
        
        if not analysis.get("alert"):
            print("✅ Activité solaire normale")
            return {"status": "ok", "message": "Pas d'anomalie détectée"}
        
        print(f"⚠️  ALERTE DÉTECTÉE: {analysis['level_name']}")
        
        # Vérifier si on doit enregistrer l'alerte
        if self.should_send_alert(analysis["level"]):
            # Enregistrer l'alerte
            self.log_alert(analysis)
            
            return {
                "status": "alert_logged",
                "analysis": analysis
            }
        else:
            print("⏭️  Alerte non enregistrée (cooldown ou niveau insuffisant)")
            return {
                "status": "alert_suppressed",
                "analysis": analysis
            }


def main():
    """Point d'entrée principal du script."""
    import sys
    
    # Vérifier si on est en mode check-only (pour GitHub Actions)
    check_only = '--check-only' in sys.argv
    
    alert_system = SolarAlertSystem()
    
    if check_only:
        # Mode GitHub Actions: juste analyser sans envoyer d'emails
        print("🔍 Mode vérification activé (pas d'envoi d'email)")
        
        # Récupérer et analyser les données
        data = alert_system.fetch_current_proton_data()
        if not data:
            print("❌ Impossible de récupérer les données")
            sys.exit(1)
        
        analysis = alert_system.analyze_data(data)
        
        if analysis.get("alert"):
            print(f"\n🚨 ALERTE DÉTECTÉE !")
            print(f"Niveau: {analysis['level_name']}")
            print(f"\nDétails par énergie:")
            for detail in analysis['details']:
                print(f"  - ≥{detail['energy']} MeV: {detail['flux']:.2f} pfu")
                print(f"    Niveau: {detail['name']}")
                print(f"    Impact: {detail['description']}")
            sys.exit(1)  # Code de sortie non-zéro pour signaler une alerte
        else:
            print("\n✅ Aucune anomalie détectée dans l'activité solaire.")
            print("   Lectures actuelles:")
            for energy, reading in analysis.get('latest_readings', {}).items():
                print(f"   - ≥{energy} MeV: {reading['flux']:.2f} pfu")
            sys.exit(0)
    else:
        # Mode normal: analyser et envoyer des emails si nécessaire
        result = alert_system.check_and_alert()
        
        print("\n" + "="*50)
        print("RÉSULTAT:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="*50)


if __name__ == "__main__":
    main()

