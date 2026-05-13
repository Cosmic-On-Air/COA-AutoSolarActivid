/**
 * Widget d'Alerte Solaire COA
 * 
 * Widget JavaScript autonome pour afficher les alertes d'activité solaire
 * sur n'importe quel site web.
 * 
 * Usage:
 * 1. Hébergez solar_alert_api.py sur un serveur
 * 2. Incluez ce script dans votre page HTML:
 *    <script src="solar_alert_widget.js"></script>
 * 3. Initialisez le widget:
 *    <script>
 *      SolarAlertWidget.init({
 *        apiUrl: 'http://votre-serveur.com:5000',
 *        checkInterval: 300000, // 5 minutes
 *        position: 'top-right'
 *      });
 *    </script>
 */

(function() {
    'use strict';
    
    const SolarAlertWidget = {
        config: {
            apiUrl: 'http://localhost:5000',
            checkInterval: 300000, // 5 minutes par défaut
            position: 'top-right', // top-right, top-left, bottom-right, bottom-left
            autoShow: true,
            showNormalStatus: false
        },
        
        currentAlert: null,
        
        init: function(options) {
            // Fusionner les options avec la configuration par défaut
            Object.assign(this.config, options || {});
            
            // Injecter les styles CSS
            this.injectStyles();
            
            // Créer le conteneur du widget
            this.createWidget();
            
            // Première vérification
            this.checkSolarActivity();
            
            // Vérifications périodiques
            setInterval(() => this.checkSolarActivity(), this.config.checkInterval);
            
            console.log('🌞 Widget d\'alerte solaire initialisé');
        },
        
        injectStyles: function() {
            const styles = `
                .solar-alert-widget {
                    position: fixed;
                    z-index: 99999;
                    max-width: 400px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }
                
                .solar-alert-widget.top-right {
                    top: 20px;
                    right: 20px;
                }
                
                .solar-alert-widget.top-left {
                    top: 20px;
                    left: 20px;
                }
                
                .solar-alert-widget.bottom-right {
                    bottom: 20px;
                    right: 20px;
                }
                
                .solar-alert-widget.bottom-left {
                    bottom: 20px;
                    left: 20px;
                }
                
                .solar-alert-badge {
                    cursor: pointer;
                    padding: 12px 20px;
                    border-radius: 25px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-weight: bold;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    transition: transform 0.3s, box-shadow 0.3s;
                }
                
                .solar-alert-badge:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
                }
                
                .solar-alert-badge.alert {
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0%, 100% {
                        box-shadow: 0 4px 15px rgba(255,0,0,0.4);
                    }
                    50% {
                        box-shadow: 0 4px 25px rgba(255,0,0,0.7);
                    }
                }
                
                .solar-alert-icon {
                    font-size: 1.5em;
                }
                
                .solar-alert-popup {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.7);
                    z-index: 100000;
                    animation: fadeIn 0.3s;
                }
                
                .solar-alert-popup.show {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                
                .solar-alert-popup-content {
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
                
                .solar-alert-header {
                    text-align: center;
                    margin-bottom: 20px;
                    padding: 20px;
                    border-radius: 8px;
                    color: white;
                }
                
                .solar-alert-header h2 {
                    margin: 10px 0;
                    font-size: 2em;
                }
                
                .solar-alert-detail {
                    background: #f8f9fa;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 6px;
                    border-left: 4px solid;
                }
                
                .solar-alert-close {
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
                
                .solar-alert-close:hover {
                    background: #5a6268;
                }
                
                .solar-readings {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 10px;
                    margin: 15px 0;
                }
                
                .solar-reading-card {
                    background: white;
                    padding: 12px;
                    border-radius: 6px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }
                
                .solar-reading-card strong {
                    display: block;
                    color: #667eea;
                    margin-bottom: 5px;
                }
            `;
            
            const styleSheet = document.createElement('style');
            styleSheet.textContent = styles;
            document.head.appendChild(styleSheet);
        },
        
        createWidget: function() {
            // Badge principal
            const badge = document.createElement('div');
            badge.className = `solar-alert-widget ${this.config.position}`;
            badge.innerHTML = `
                <div class="solar-alert-badge" id="solar-badge">
                    <span class="solar-alert-icon">🌞</span>
                    <span class="solar-alert-text">Activité solaire</span>
                </div>
            `;
            document.body.appendChild(badge);
            
            // Pop-up
            const popup = document.createElement('div');
            popup.className = 'solar-alert-popup';
            popup.id = 'solar-popup';
            popup.innerHTML = `
                <div class="solar-alert-popup-content" id="solar-popup-content">
                    <!-- Contenu dynamique -->
                </div>
            `;
            document.body.appendChild(popup);
            
            // Events
            document.getElementById('solar-badge').addEventListener('click', () => {
                this.showPopup();
            });
            
            popup.addEventListener('click', (e) => {
                if (e.target === popup) {
                    this.hidePopup();
                }
            });
        },
        
        async checkSolarActivity() {
            try {
                const response = await fetch(`${this.config.apiUrl}/api/status`);
                const data = await response.json();
                
                this.currentAlert = data;
                this.updateBadge(data);
                
                // Afficher automatiquement si nouvelle alerte
                if (data.alert && this.config.autoShow) {
                    if (!this.hasSeenAlert(data)) {
                        this.showPopup();
                        this.markAlertAsSeen(data);
                    }
                }
            } catch (error) {
                console.error('Erreur lors de la vérification de l\'activité solaire:', error);
            }
        },
        
        updateBadge: function(data) {
            const badge = document.getElementById('solar-badge');
            const icon = badge.querySelector('.solar-alert-icon');
            const text = badge.querySelector('.solar-alert-text');
            
            if (data.alert) {
                badge.classList.add('alert');
                icon.textContent = '⚠️';
                text.textContent = data.level_name || 'ALERTE';
            } else {
                badge.classList.remove('alert');
                icon.textContent = '🌞';
                text.textContent = 'Activité normale';
                
                if (!this.config.showNormalStatus) {
                    badge.parentElement.style.display = 'none';
                }
            }
        },
        
        showPopup: function() {
            if (!this.currentAlert) return;
            
            const popup = document.getElementById('solar-popup');
            const content = document.getElementById('solar-popup-content');
            
            if (this.currentAlert.alert) {
                content.innerHTML = this.renderAlertContent(this.currentAlert);
            } else {
                content.innerHTML = this.renderNormalContent(this.currentAlert);
            }
            
            popup.classList.add('show');
        },
        
        hidePopup: function() {
            const popup = document.getElementById('solar-popup');
            popup.classList.remove('show');
        },
        
        renderAlertContent: function(data) {
            const levelColors = {
                'S1_MINOR': '#FFD700',
                'S2_MODERATE': '#FFA500',
                'S3_STRONG': '#FF8C00',
                'S4_SEVERE': '#FF4500',
                'S5_EXTREME': '#FF0000'
            };
            
            const levelIcons = {
                'S1_MINOR': '⚠️',
                'S2_MODERATE': '⚠️',
                'S3_STRONG': '🔶',
                'S4_SEVERE': '🔴',
                'S5_EXTREME': '🚨'
            };
            
            const color = levelColors[data.level] || '#FFD700';
            const icon = levelIcons[data.level] || '⚠️';
            
            let detailsHtml = '';
            if (data.details) {
                data.details.forEach(detail => {
                    detailsHtml += `
                        <div class="solar-alert-detail" style="border-left-color: ${detail.color}">
                            <strong>${detail.name}</strong>
                            <p>Énergie: ≥${detail.energy} MeV</p>
                            <p>Flux: ${detail.flux.toFixed(2)} protons·cm⁻²·s⁻¹·sr⁻¹</p>
                            <p style="font-style: italic;">${detail.description}</p>
                        </div>
                    `;
                });
            }
            
            let readingsHtml = '';
            if (data.latest_readings) {
                readingsHtml = '<h3 style="margin-top: 20px;">Lectures actuelles:</h3><div class="solar-readings">';
                for (const [energy, reading] of Object.entries(data.latest_readings)) {
                    readingsHtml += `
                        <div class="solar-reading-card">
                            <strong>≥${energy} MeV</strong>
                            <div>${reading.flux.toFixed(2)} pfu</div>
                        </div>
                    `;
                }
                readingsHtml += '</div>';
            }
            
            return `
                <div class="solar-alert-header" style="background: linear-gradient(135deg, ${color} 0%, #ff6b6b 100%);">
                    <div style="font-size: 3em;">${icon}</div>
                    <h2>ALERTE SOLAIRE</h2>
                    <p>${data.level_name}</p>
                </div>
                
                <div>
                    <h3>Anomalies détectées:</h3>
                    ${detailsHtml}
                </div>
                
                ${readingsHtml}
                
                <p style="text-align: center; margin-top: 20px;">
                    <a href="https://www.swpc.noaa.gov/" target="_blank" 
                       style="display: inline-block; padding: 12px 24px; background: #667eea; color: white; 
                              text-decoration: none; border-radius: 6px; font-weight: bold;">
                        🔗 Plus d'infos sur NOAA
                    </a>
                </p>
                
                <button class="solar-alert-close" onclick="SolarAlertWidget.hidePopup()">
                    Fermer
                </button>
            `;
        },
        
        renderNormalContent: function(data) {
            let readingsHtml = '';
            if (data.latest_readings) {
                readingsHtml = '<div class="solar-readings">';
                for (const [energy, reading] of Object.entries(data.latest_readings)) {
                    readingsHtml += `
                        <div class="solar-reading-card">
                            <strong>≥${energy} MeV</strong>
                            <div>${reading.flux.toFixed(2)} pfu</div>
                        </div>
                    `;
                }
                readingsHtml += '</div>';
            }
            
            return `
                <div class="solar-alert-header" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
                    <div style="font-size: 3em;">✅</div>
                    <h2>Activité Solaire Normale</h2>
                </div>
                
                <p style="text-align: center; margin: 20px 0;">
                    Aucune anomalie détectée dans les flux de protons solaires.
                </p>
                
                <h3 style="margin-top: 20px;">Lectures actuelles:</h3>
                ${readingsHtml}
                
                <button class="solar-alert-close" onclick="SolarAlertWidget.hidePopup()">
                    Fermer
                </button>
            `;
        },
        
        hasSeenAlert: function(data) {
            if (!data.alert) return true;
            
            const lastSeen = localStorage.getItem('solar_alert_last_seen');
            if (!lastSeen) return false;
            
            const lastSeenData = JSON.parse(lastSeen);
            return lastSeenData.level === data.level && 
                   lastSeenData.timestamp === data.timestamp;
        },
        
        markAlertAsSeen: function(data) {
            if (!data.alert) return;
            
            localStorage.setItem('solar_alert_last_seen', JSON.stringify({
                level: data.level,
                timestamp: data.timestamp
            }));
        }
    };
    
    // Exposer globalement
    window.SolarAlertWidget = SolarAlertWidget;
})();
