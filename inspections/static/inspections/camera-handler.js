/**
 * محسّن التقاط الصور والكاميرا
 * Camera and Image Capture Handler
 * 
 * يحسّن عملية التقاط الصور على جميع الأجهزة
 * خاصة هواتف Huawei و Android
 */

(function() {
    'use strict';
    
    // تحديد نوع الجهاز والمتصفح
    const userAgent = navigator.userAgent.toLowerCase();
    const isHuawei = /huawei|honor/.test(userAgent);
    const isAndroid = /android/.test(userAgent);
    const isIOS = /iphone|ipad|ipod/.test(userAgent);
    const isSamsung = /samsung/.test(userAgent);
    const isChrome = /chrome|chromium/.test(userAgent);
    const isFirefox = /firefox/.test(userAgent);
    const isSafari = /safari/.test(userAgent) && !isChrome;
    
    console.log('🔍 Device Detection:', { isHuawei, isAndroid, isIOS, isSamsung, isChrome, isFirefox, isSafari });
    
    // معالجة الأزرار - simplified approach
    function setupCameraHandlers() {
        console.log('🎯 Setting up camera handlers...');
        
        // Configure file input accept attributes based on device
        if (isHuawei || isAndroid) {
            console.log('⚙️ Configuring for Android/Huawei device');
            document.querySelectorAll("input[type='file'][accept*='image']").forEach(input => {
                input.setAttribute('accept', 'image/*');
            });
        }
        
        if (isIOS) {
            console.log('⚙️ Configuring for iOS device');
            document.querySelectorAll("input[type='file'][capture]").forEach(input => {
                input.setAttribute('accept', 'image/*');
            });
        }
    }
    
    /**
     * تحسينات خاصة لهواتف Huawei
     */
    function applyHuaweiOptimizations() {
        if (!isHuawei) return;
        
        console.log('🔧 Applying Huawei optimizations...');
        
        document.querySelectorAll(".image-camera-input, .image-camera-input-fallback").forEach(input => {
            input.setAttribute('accept', 'image/*');
        });
    }
    
    /**
     * معالج خطأ الكاميرا
     */
    function handleCameraError(message) {
        console.error('❌ Camera error:', message);
        showCameraError(message);
    }
    /**
     * عرض رسالة خطأ
     */
    function showCameraError(message) {
        console.error('⚠️ Camera Error:', message);
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'camera-error-alert';
        alertDiv.setAttribute('role', 'alert');
        alertDiv.setAttribute('aria-live', 'polite');
        alertDiv.innerHTML = `
            <div class="error-content">
                <strong>⚠️ خطأ الكاميرا/المعرج</strong>
                <p>${message}</p>
                <button type="button" class="btn btn-sm" onclick="this.parentElement.parentElement.remove()">إغلاق</button>
            </div>
        `;
        
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    /**
     * التحقق من دعم الكاميرا
     */
    function checkCameraSupport() {
        const hasCamera = navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
        console.log('📹 Camera API support:', hasCamera ? '✅ Yes' : '❌ No');
        
        const input = document.createElement('input');
        input.setAttribute('type', 'file');
        const hasInputCapture = 'capture' in input;
        console.log('📹 Input capture support:', hasInputCapture ? '✅ Yes' : '❌ No');
    }
    
    /**
     * تهيئة التطبيق
     */
    function initialize() {
        console.log('🚀 Initializing Camera Handler...');
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupAll);
        } else {
            setupAll();
        }
    }
    
    function setupAll() {
        try {
            checkCameraSupport();
            setupCameraHandlers();
            applyHuaweiOptimizations();
            console.log('✅ Camera Handler initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing camera handler:', error);
        }
    }
    
    // Start initialization
    initialize();
    
    // إضافة أسلوب للتنبيهات
    if (!document.getElementById('camera-error-styles')) {
        const style = document.createElement('style');
        style.id = 'camera-error-styles';
        style.textContent = `
            .camera-error-alert {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #fff3cd;
                border: 2px solid #ff9800;
                border-radius: 8px;
                padding: 16px;
                max-width: 90%;
                z-index: 9999;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            .camera-error-alert .error-content {
                font-family: 'Cairo', Tahoma, sans-serif;
                direction: rtl;
            }
            
            .camera-error-alert strong {
                color: #f57f17;
                display: block;
                margin-bottom: 8px;
            }
            
            .camera-error-alert p {
                margin: 8px 0;
                color: #333;
            }
            
            .camera-error-alert .btn {
                margin-top: 8px;
                padding: 6px 12px;
                font-size: 12px;
            }
            
            @media (max-width: 600px) {
                .camera-error-alert {
                    left: 20px;
                    right: 20px;
                    top: 20px;
                    max-width: calc(100% - 40px);
                }
            }
        `;
        document.head.appendChild(style);
    }
})();
