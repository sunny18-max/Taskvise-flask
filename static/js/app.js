// TaskVise App JavaScript

function initMobileNav() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    const navToggle = navbar.querySelector('.mobile-nav-toggle');
    const navActions = navbar.querySelector('.nav-actions');
    if (!navToggle || !navActions) return;

    const mobileBreakpoint = 900;
    const isMobileView = () => window.innerWidth <= mobileBreakpoint;

    if (!navActions.id) {
        navActions.id = 'mobileNavActions';
    }
    navToggle.setAttribute('aria-controls', navActions.id);
    navToggle.setAttribute('aria-expanded', 'false');

    let backdrop = document.querySelector('.nav-backdrop[data-nav-backdrop="global"]');
    if (!backdrop) {
        backdrop = document.createElement('button');
        backdrop.type = 'button';
        backdrop.className = 'nav-backdrop';
        backdrop.setAttribute('aria-label', 'Close navigation');
        backdrop.setAttribute('data-nav-backdrop', 'global');
        document.body.appendChild(backdrop);
    }

    const closeMenu = () => {
        navActions.classList.remove('open');
        navToggle.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
        backdrop.classList.remove('show');
        document.body.classList.remove('mobile-nav-open');
    };

    const openMenu = () => {
        if (!isMobileView()) return;
        navActions.classList.add('open');
        navToggle.classList.add('active');
        navToggle.setAttribute('aria-expanded', 'true');
        backdrop.classList.add('show');
        document.body.classList.add('mobile-nav-open');
    };

    navToggle.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (navActions.classList.contains('open')) {
            closeMenu();
            return;
        }
        openMenu();
    });

    backdrop.addEventListener('click', closeMenu);

    document.addEventListener('click', (event) => {
        if (!navActions.classList.contains('open')) return;
        if (navActions.contains(event.target) || navToggle.contains(event.target)) return;
        closeMenu();
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeMenu();
        }
    });

    navActions.querySelectorAll('a, button').forEach((item) => {
        item.addEventListener('click', () => {
            if (isMobileView()) closeMenu();
        });
    });

    window.addEventListener('resize', () => {
        if (!isMobileView()) closeMenu();
    });
}

// Initialize AOS animations
document.addEventListener('DOMContentLoaded', function() {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            once: true,
            offset: 100
        });
    }

    initMobileNav();
    
    // Add any additional initialization code here
    console.log('TaskVise app initialized');

    // Show loader when any internal link is clicked
    function showRouteLoader() {
        const preloader = document.getElementById('preloader');
        if (preloader) {
            preloader.classList.remove('hidden');
        }
    }

    document.querySelectorAll('a').forEach(link => {
        const href = link.getAttribute('href');
        if (!href || href.startsWith('http') || href.startsWith('#') || href.startsWith('mailto:')) {
            return;
        }
        link.addEventListener('click', function(event) {
            if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            showRouteLoader();
        });
    });
});

// Form validation helper functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^\d{10}$/;
    return re.test(phone);
}

// Utility function to show notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add styles for notification
    if (!document.querySelector('.notification-styles')) {
        const styles = document.createElement('style');
        styles.className = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 100px;
                right: 20px;
                background: white;
                padding: 1rem 1.5rem;
                border-radius: 0.5rem;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                border-left: 4px solid #3b82f6;
                z-index: 10000;
                max-width: 400px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                animation: slideInRight 0.3s ease-out;
            }
            .notification-success { border-left-color: #10b981; }
            .notification-error { border-left-color: #ef4444; }
            .notification-warning { border-left-color: #f59e0b; }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .notification-close {
                background: none;
                border: none;
                color: #64748b;
                cursor: pointer;
                padding: 0.25rem;
                border-radius: 0.25rem;
            }
            .notification-close:hover {
                background: #f8fafc;
            }
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}
