"""
API Web pour les alertes solaires
Fournit un endpoint REST pour vérifier l'activité solaire et afficher des pop-ups sur un site web.

Usage:
    python solar_alert_api.py

Endpoints:
    GET /api/status - État actuel de l'activité solaire
    GET /api/history - Historique des alertes (7 derniers jours)
    GET / - Page de démonstration avec pop-up
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from solar_alert_system import SolarAlertSystem, ALERT_LEVELS, ALERT_THRESHOLDS

app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin

# Instance du système d'alerte
alert_system = SolarAlertSystem()

@app.route('/api/status')
def get_status():
    """
    Retourne l'état actuel de l'activité solaire.
    
    Returns:
        JSON: {
            "alert": bool,
            "level": str (si alerte),
            "level_name": str (si alerte),
            "details": list (si alerte),
            "latest_readings": dict,
            "timestamp": str
        }
    """
    try:
        data = alert_system.fetch_current_proton_data()
        
        if not data:
            return jsonify({
                "error": "Impossible de récupérer les données",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 503
        
        analysis = alert_system.analyze_data(data)
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@app.route('/api/history')
def get_history():
    """
    Retourne l'historique des alertes des 7 derniers jours.
    
    Returns:
        JSON: {
            "alerts": list,
            "count": int,
            "period": str
        }
    """
    try:
        history = alert_system.load_alert_history()
        
        # Filtrer les 7 derniers jours
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        recent_alerts = []
        
        for alert in history:
            alert_time = datetime.fromisoformat(alert["timestamp"])
            if alert_time > cutoff:
                recent_alerts.append(alert)
        
        return jsonify({
            "alerts": recent_alerts,
            "count": len(recent_alerts),
            "period": "7 derniers jours"
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@app.route('/api/thresholds')
def get_thresholds():
    """
    Retourne les seuils d'alerte configurés.
    
    Returns:
        JSON: {
            "thresholds": dict,
            "levels": dict
        }
    """
    return jsonify({
        "thresholds": ALERT_THRESHOLDS,
        "levels": ALERT_LEVELS
    })


@app.route('/')
def demo_page():
    """
    Page de démonstration avec pop-up d'alerte solaire.
    """
    html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Surveillance Solaire - COA-AutoSolarActivid</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            width: 100%;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            margin: 20px 0;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .status-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #28a745;
        }
        
        .status-card.alert {
            border-left-color: #dc3545;
            background: #fff5f5;
        }
        
        .status-card h2 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .readings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .reading-card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .reading-card strong {
            display: block;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #5568d3;
        }
        
        .btn-refresh {
            background: #28a745;
        }
        
        .btn-refresh:hover {
            background: #218838;
        }
        
        /* Pop-up d'alerte */
        .alert-popup {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            animation: fadeIn 0.3s;
        }
        
        .alert-popup.show {
            display: flex;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .alert-content {
            background: white;
            border-radius: 12px;
            padding: 30px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            animation: slideUp 0.3s;
        }
        
        @keyframes slideUp {
            from {
                transform: translateY(50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        .alert-header {
            text-align: center;
            margin-bottom: 20px;
            padding: 20px;
            border-radius: 8px;
            color: white;
        }
        
        .alert-header h2 {
            margin: 10px 0;
            font-size: 2em;
        }
        
        .alert-details {
            margin: 20px 0;
        }
        
        .detail-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
            border-left: 4px solid;
        }
        
        .close-btn {
            display: block;
            width: 100%;
            padding: 15px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 20px;
        }
        
        .close-btn:hover {
            background: #5a6268;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .last-update {
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌞 Surveillance de l'Activité Solaire</h1>
        <p class="subtitle">Détection en temps réel des tempêtes de radiation</p>
        
        <div class="button-group">
            <button class="btn btn-refresh" onclick="checkSolarActivity()">
                🔄 Actualiser
            </button>
            <button class="btn" onclick="showHistory()">
                📊 Historique
            </button>
        </div>
        
        <div id="status-container">
            <div class="loading">
                <div class="spinner"></div>
                <p>Chargement des données...</p>
            </div>
        </div>
        
        <div class="last-update" id="last-update"></div>
    </div>
    
    <!-- Pop-up d'alerte -->
    <div class="alert-popup" id="alert-popup">
        <div class="alert-content" id="alert-content">
            <!-- Contenu dynamique -->
        </div>
    </div>
    
    <script>
        let currentData = null;
        
        async function checkSolarActivity() {
            const container = document.getElementById('status-container');
            container.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Vérification de l'activité solaire...</p>
                </div>
            `;
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                currentData = data;
                
                displayStatus(data);
                
                // Afficher le pop-up si alerte
                if (data.alert) {
                    showAlertPopup(data);
                }
                
                updateLastUpdate();
            } catch (error) {
                container.innerHTML = `
                    <div class="status-card alert">
                        <h2>❌ Erreur</h2>
                        <p>Impossible de récupérer les données: ${error.message}</p>
                    </div>
                `;
            }
        }
        
        function displayStatus(data) {
            const container = document.getElementById('status-container');
            
            if (data.alert) {
                let detailsHtml = '';
                data.details.forEach(detail => {
                    detailsHtml += `
                        <div class="detail-item" style="border-left-color: ${detail.color}">
                            <strong>${detail.name} - ≥${detail.energy} MeV</strong>
                            <p>Flux: ${detail.flux.toFixed(2)} protons·cm⁻²·s⁻¹·sr⁻¹</p>
                            <p><em>${detail.description}</em></p>
                        </div>
                    `;
                });
                
                container.innerHTML = `
                    <div class="status-card alert">
                        <h2>⚠️ ALERTE: ${data.level_name}</h2>
                        <p>Une activité solaire anormale a été détectée.</p>
                        <div class="alert-details">
                            ${detailsHtml}
                        </div>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="status-card">
                        <h2>✅ Activité normale</h2>
                        <p>Aucune anomalie détectée dans les flux de protons solaires.</p>
                    </div>
                `;
            }
            
            // Ajouter les lectures actuelles
            if (data.latest_readings) {
                let readingsHtml = '<h3 style="margin-top: 20px;">Lectures actuelles:</h3><div class="readings-grid">';
                for (const [energy, reading] of Object.entries(data.latest_readings)) {
                    readingsHtml += `
                        <div class="reading-card">
                            <strong>≥${energy} MeV</strong>
                            <div>${reading.flux.toFixed(2)} pfu</div>
                        </div>
                    `;
                }
                readingsHtml += '</div>';
                container.innerHTML += readingsHtml;
            }
        }
        
        function showAlertPopup(data) {
            const popup = document.getElementById('alert-popup');
            const content = document.getElementById('alert-content');
            
            const level = data.level || 'S1_MINOR';
            const levelData = {
                'S1_MINOR': { color: '#FFD700', icon: '⚠️' },
                'S2_MODERATE': { color: '#FFA500', icon: '⚠️' },
                'S3_STRONG': { color: '#FF8C00', icon: '🔶' },
                'S4_SEVERE': { color: '#FF4500', icon: '🔴' },
                'S5_EXTREME': { color: '#FF0000', icon: '🚨' }
            };
            
            const currentLevel = levelData[level] || levelData['S1_MINOR'];
            
            let detailsHtml = '';
            data.details.forEach(detail => {
                detailsHtml += `
                    <div class="detail-item" style="border-left-color: ${detail.color}">
                        <strong>${detail.name}</strong>
                        <p>Énergie: ≥${detail.energy} MeV</p>
                        <p>Flux: ${detail.flux.toFixed(2)} protons·cm⁻²·s⁻¹·sr⁻¹</p>
                        <p><em>${detail.description}</em></p>
                        <p style="font-size: 0.9em; color: #666;">Détecté: ${new Date(detail.time).toLocaleString('fr-FR')}</p>
                    </div>
                `;
            });
            
            content.innerHTML = `
                <div class="alert-header" style="background: linear-gradient(135deg, ${currentLevel.color} 0%, #ff6b6b 100%);">
                    <div style="font-size: 3em;">${currentLevel.icon}</div>
                    <h2>ALERTE SOLAIRE</h2>
                    <p>${data.level_name}</p>
                </div>
                
                <div class="alert-details">
                    <h3>Anomalies détectées:</h3>
                    ${detailsHtml}
                </div>
                
                <p style="text-align: center; margin-top: 20px;">
                    <a href="https://www.swpc.noaa.gov/" target="_blank" class="btn">
                        🔗 Consulter NOAA SWPC
                    </a>
                </p>
                
                <button class="close-btn" onclick="closePopup()">Fermer</button>
            `;
            
            popup.classList.add('show');
        }
        
        function closePopup() {
            const popup = document.getElementById('alert-popup');
            popup.classList.remove('show');
        }
        
        async function showHistory() {
            try {
                const response = await fetch('/api/history');
                const data = await response.json();
                
                const popup = document.getElementById('alert-popup');
                const content = document.getElementById('alert-content');
                
                let historyHtml = '';
                if (data.alerts && data.alerts.length > 0) {
                    data.alerts.reverse().forEach(alert => {
                        historyHtml += `
                            <div class="detail-item" style="border-left-color: #667eea">
                                <strong>${alert.level_name}</strong>
                                <p>${new Date(alert.timestamp).toLocaleString('fr-FR')}</p>
                            </div>
                        `;
                    });
                } else {
                    historyHtml = '<p style="text-align: center; color: #666;">Aucune alerte dans les 7 derniers jours</p>';
                }
                
                content.innerHTML = `
                    <h2 style="text-align: center; margin-bottom: 20px;">📊 Historique des alertes</h2>
                    <p style="text-align: center; color: #666; margin-bottom: 20px;">${data.period}</p>
                    <div class="alert-details">
                        ${historyHtml}
                    </div>
                    <button class="close-btn" onclick="closePopup()">Fermer</button>
                `;
                
                popup.classList.add('show');
            } catch (error) {
                alert('Erreur lors de la récupération de l\'historique: ' + error.message);
            }
        }
        
        function updateLastUpdate() {
            const element = document.getElementById('last-update');
            element.textContent = `Dernière mise à jour: ${new Date().toLocaleString('fr-FR')}`;
        }
        
        // Vérification automatique toutes les 5 minutes
        setInterval(checkSolarActivity, 5 * 60 * 1000);
        
        // Vérification initiale
        checkSolarActivity();
    </script>
</body>
</html>
    """
    return render_template_string(html_template)


if __name__ == '__main__':
    print("🌐 Démarrage du serveur API d'alertes solaires...")
    print("📡 URL de l'API: http://localhost:5000/api/status")
    print("🌍 Page de démonstration: http://localhost:5000/")
    print("\nAppuyez sur Ctrl+C pour arrêter le serveur.\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
