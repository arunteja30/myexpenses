// Progressive Web App functionality
let deferredPrompt;

// Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

// PWA Install Prompt
window.addEventListener('beforeinstallprompt', (e) => {
    console.log('PWA install prompt triggered');
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    // Show install button if it exists
    showInstallButton();
});

function showInstallButton() {
    const installButton = document.getElementById('install-button');
    if (installButton) {
        installButton.style.display = 'block';
    } else {
        // Create and show install banner
        createInstallBanner();
    }
}

function createInstallBanner() {
    if (document.getElementById('install-banner')) return; // Already exists
    
    const banner = document.createElement('div');
    banner.id = 'install-banner';
    banner.className = 'alert alert-info alert-dismissible fade show position-fixed';
    banner.style.cssText = 'top: 80px; left: 10px; right: 10px; z-index: 1050;';
    banner.innerHTML = `
        <strong>Install App</strong> Add Expense Manager to your home screen for quick access!
        <button type="button" class="btn btn-sm btn-primary ms-2" onclick="triggerInstall()">Install</button>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(banner);
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        if (banner && banner.parentNode) {
            banner.remove();
        }
    }, 10000);
}

function triggerInstall() {
    const banner = document.getElementById('install-banner');
    if (banner) banner.remove();
    
    if (deferredPrompt) {
        // Show the install prompt
        deferredPrompt.prompt();
        // Wait for the user to respond to the prompt
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
            } else {
                console.log('User dismissed the install prompt');
            }
            deferredPrompt = null;
        });
    }
}

// Check if app is already installed
window.addEventListener('appinstalled', (evt) => {
    console.log('PWA was installed');
    const banner = document.getElementById('install-banner');
    if (banner) banner.remove();
});
// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const body = document.getElementById('app-body');
    const themeIcon = document.getElementById('theme-icon');
    
    if (savedTheme === 'dark') {
        body.setAttribute('data-bs-theme', 'dark');
        if (themeIcon) {
            themeIcon.className = 'bi bi-sun';
            themeIcon.parentElement.innerHTML = '<i class="bi bi-sun" id="theme-icon"></i> Light Mode';
        }
    }
}

function toggleTheme() {
    const body = document.getElementById('app-body');
    const themeIcon = document.getElementById('theme-icon');
    const currentTheme = body.getAttribute('data-bs-theme');
    
    if (currentTheme === 'dark') {
        body.setAttribute('data-bs-theme', 'light');
        localStorage.setItem('theme', 'light');
        if (themeIcon) {
            themeIcon.className = 'bi bi-moon';
            themeIcon.parentElement.innerHTML = '<i class="bi bi-moon" id="theme-icon"></i> Dark Mode';
        }
    } else {
        body.setAttribute('data-bs-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        if (themeIcon) {
            themeIcon.className = 'bi bi-sun';
            themeIcon.parentElement.innerHTML = '<i class="bi bi-sun" id="theme-icon"></i> Light Mode';
        }
    }
}

// Install PWA prompt - using existing deferredPrompt variable
window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later.
    deferredPrompt = e;
    
    // Show install button if not already installed
    if (!window.matchMedia('(display-mode: standalone)').matches) {
        showInstallPrompt();
    }
});

function showInstallPrompt() {
    // Create install banner
    const installBanner = document.createElement('div');
    installBanner.className = 'alert alert-info alert-dismissible fade show position-fixed';
    installBanner.style.cssText = 'top: 80px; left: 10px; right: 10px; z-index: 1050;';
    installBanner.innerHTML = `
        <i class="bi bi-download me-2"></i>
        <strong>Install App:</strong> Add to your home screen for better experience!
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <div class="mt-2">
            <button class="btn btn-sm btn-primary me-2" onclick="installApp()">Install</button>
            <button class="btn btn-sm btn-outline-secondary" onclick="dismissInstall()">Not now</button>
        </div>
    `;
    document.body.appendChild(installBanner);
    
    // Auto dismiss after 10 seconds
    setTimeout(() => {
        if (installBanner.parentNode) {
            installBanner.remove();
        }
    }, 10000);
}

function installApp() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the A2HS prompt');
            }
            deferredPrompt = null;
        });
    }
    dismissInstall();
}

function dismissInstall() {
    const banner = document.querySelector('.alert');
    if (banner) {
        banner.remove();
    }
    localStorage.setItem('installPromptDismissed', 'true');
}

// Touch gestures for better mobile experience
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', e => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', e => {
    touchEndX = e.changedTouches[0].screenX;
    handleGesture();
});

function handleGesture() {
    const threshold = 100;
    const swipeRight = touchEndX > touchStartX + threshold;
    const swipeLeft = touchEndX < touchStartX - threshold;
    
    // Add swipe navigation if needed
    if (swipeRight && window.history.length > 1) {
        // Optional: Go back on swipe right
        // window.history.back();
    }
}

// Form enhancements
function enhanceForms() {
    // Auto-format currency inputs
    document.querySelectorAll('input[type="number"][step="0.01"]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
    
    // Auto-save form data to localStorage for recovery
    document.querySelectorAll('form').forEach(form => {
        const formId = form.id || form.action.split('/').pop();
        
        // Load saved data
        const savedData = localStorage.getItem(`form_${formId}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && input.type !== 'password') {
                        input.value = data[key];
                    }
                });
            } catch (e) {
                console.log('Error loading saved form data');
            }
        }
        
        // Save data on input
        form.addEventListener('input', function() {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                if (key !== 'password') {
                    data[key] = value;
                }
            }
            localStorage.setItem(`form_${formId}`, JSON.stringify(data));
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            localStorage.removeItem(`form_${formId}`);
        });
    });
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 80px; right: 10px; z-index: 1060; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// Network status monitoring
function initNetworkMonitoring() {
    function updateOnlineStatus() {
        const status = navigator.onLine ? 'online' : 'offline';
        
        if (status === 'offline') {
            showNotification(
                '<i class="bi bi-wifi-off me-2"></i>You are offline. Some features may be limited.',
                'warning',
                0 // Don't auto-dismiss
            );
        } else {
            // Remove offline notification
            document.querySelectorAll('.alert-warning').forEach(alert => {
                if (alert.textContent.includes('offline')) {
                    alert.remove();
                }
            });
        }
    }
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
}

// Enhanced number formatting
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Lazy loading for better performance
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    enhanceForms();
    initNetworkMonitoring();
    initLazyLoading();
    
    // Show install prompt if not dismissed and not installed
    if (!localStorage.getItem('installPromptDismissed') && 
        !window.matchMedia('(display-mode: standalone)').matches) {
        setTimeout(showInstallPrompt, 3000);
    }
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const timing = performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            
            if (loadTime > 3000) {
                console.log('Page load time is slow:', loadTime + 'ms');
            }
        }, 0);
    });
}

// Export functions for global use
window.toggleTheme = toggleTheme;
window.installApp = installApp;
window.dismissInstall = dismissInstall;
window.showNotification = showNotification;
window.formatCurrency = formatCurrency;
