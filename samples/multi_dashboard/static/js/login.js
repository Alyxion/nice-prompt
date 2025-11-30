/**
 * Login page back button handler.
 * Prevents back-button loop when redirected to login from a protected page.
 */

function setupLoginBackHandler() {
    // Clean up any existing handler first
    cleanupLoginBackHandler();
    
    // Back button handler - redirect to home
    window._loginBackHandler = function(event) {
        cleanupLoginBackHandler();
        history.replaceState(null, "", "/");
        location.href = "/";
    };
    window.addEventListener('popstate', window._loginBackHandler);
    
    // Clean up when URL changes away from /login
    window._loginUrlChecker = setInterval(function() {
        if (location.pathname !== '/login') {
            cleanupLoginBackHandler();
        }
    }, 100);
}

function cleanupLoginBackHandler() {
    if (window._loginUrlChecker) {
        clearInterval(window._loginUrlChecker);
        delete window._loginUrlChecker;
    }
    if (window._loginBackHandler) {
        window.removeEventListener('popstate', window._loginBackHandler);
        delete window._loginBackHandler;
    }
}

// Export for use
window.setupLoginBackHandler = setupLoginBackHandler;
window.cleanupLoginBackHandler = cleanupLoginBackHandler;
