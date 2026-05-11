/**
 * محسّن التقاط الصور والكاميرا
 * Camera and Image Capture Handler
 * 
 * يحسّن عملية التقاط الصور على جميع الأجهزة
 * خاصة هواتف Huawei و Android
 */

(function() {
    // تحديد نوع الجهاز والمتصفح
    const userAgent = navigator.userAgent.toLowerCase();
    const isHuawei = /huawei|honor/.test(userAgent);
    const isAndroid = /android/.test(userAgent);
    const isIOS = /iphone|ipad|ipod/.test(userAgent);
    const isSamsung = /samsung/.test(userAgent);
    
    console.log('🔍 Device Detection:', { isHuawei, isAndroid, isIOS, isSamsung });
    
    // معالجة الأزرار
    function setupCameraHandlers() {
        // أزرار التقاط الصور من الكاميرا
        document.querySelectorAll(".image-camera-btn").forEach(btn => {
            btn.addEventListener("click", function(e) {
                e.preventDefault();
                handleCameraClick(this);
            });
        });
        
        // أزرار اختيار من المعرض
        document.querySelectorAll(".image-gallery-btn").forEach(btn => {
            btn.addEventListener("click", function(e) {
                e.preventDefault();
                handleGalleryClick(this);
            });
        });
    }
    
    /**
     * التعامل مع زر التقاط الصور من الكاميرا
     */
    function handleCameraClick(button) {
        const container = button.closest(".image-upload-container");
        if (!container) return;
        
        // محاولة أولاً مع environment (الكاميرا الخلفية)
        let cameraInput = container.querySelector(".image-camera-input[capture='environment']");
        const fallbackInput = container.querySelector(".image-camera-input-fallback");
        
        if (!cameraInput) {
            cameraInput = container.querySelector(".image-camera-input");
        }
        
        if (cameraInput) {
            // إضافة معالج لمحاولة fallback عند الفشل
            const handleCancel = function() {
                console.log('📸 Primary camera cancelled, trying fallback (user camera)');
                if (fallbackInput) {
                    setTimeout(() => {
                        try {
                            fallbackInput.click();
                        } catch (e) {
                            console.error('❌ Fallback click failed:', e);
                        }
                    }, 100);
                }
                cameraInput.removeEventListener('cancel', handleCancel);
                cameraInput.removeEventListener('error', handleError);
            };
            
            const handleError = function(error) {
                console.error('❌ Error with primary camera:', error);
                handleCancel();
            };
            
            cameraInput.addEventListener('cancel', handleCancel, { once: true });
            cameraInput.addEventListener('error', handleError, { once: true });
            
            // محاولة النقر على الإدخال
            try {
                cameraInput.click();
                console.log('✅ Camera input clicked successfully');
            } catch (error) {
                console.error('❌ Error clicking camera input:', error);
                handleCancel();
                showCameraError('فشل فتح الكاميرا. يرجى التحقق من الأذونات.');
            }
        } else {
            console.error('❌ Camera input not found');
            showCameraError('عنصر الكاميرا غير متاح.');
        }
    }
    
    /**
     * التعامل مع زر المعرض
     */
    function handleGalleryClick(button) {
        const container = button.closest(".image-upload-container");
        if (!container) return;
        
        const galleryInput = container.querySelector(".image-input");
        if (galleryInput) {
            try {
                galleryInput.click();
                console.log('✅ Gallery input clicked successfully');
            } catch (error) {
                console.error('❌ Error clicking gallery input:', error);
                showCameraError('فشل فتح المعرض.');
            }
        }
    }
    
    /**
     * معالج إلغاء الكاميرا
     */
    function handleCameraCancel() {
        console.log('ℹ️ Camera capture cancelled by user');
    }
    
    /**
     * معالج خطأ الكاميرا
     */
    function handleCameraError(e) {
        console.error('❌ Camera error:', e);
        const error = e.target.error?.name || 'unknown';
        
        let message = 'حدث خطأ في الكاميرا.';
        
        switch (error) {
            case 'NotAllowedError':
                message = 'لم يتم السماح بالوصول إلى الكاميرا. يرجى التحقق من الأذونات في إعدادات الجهاز.';
                break;
            case 'NotFoundError':
                message = 'لا توجد كاميرا على هذا الجهاز.';
                break;
            case 'NotReadableError':
                message = 'الكاميرا قيد الاستخدام من قبل تطبيق آخر.';
                break;
            case 'SecurityError':
                message = 'يجب استخدام HTTPS لالتقاط الصور من الكاميرا.';
                break;
        }
        
        showCameraError(message);
    }
    
    /**
     * عرض رسالة خطأ
     */
    function showCameraError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'camera-error-alert';
        alertDiv.setAttribute('role', 'alert');
        alertDiv.setAttribute('aria-live', 'polite');
        alertDiv.innerHTML = `
            <div class="error-content">
                <strong>⚠️ خطأ الكاميرا</strong>
                <p>${message}</p>
                <button type="button" class="btn btn-sm" onclick="this.parentElement.parentElement.remove()">إغلاق</button>
            </div>
        `;
        
        // إدراج التنبيه في بداية الصفحة
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        // إزالة تلقائية بعد 5 ثوان
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    /**
     * إعادة محاولة مع capture fallback
     * استخدام user بدلاً من environment إذا فشلت
     */
    function tryFallbackCapture() {
        console.log('🔄 Trying fallback capture mode (user instead of environment)');
        
        document.querySelectorAll(".image-camera-input").forEach(input => {
            // إذا كان capture="environment"، جرب إضافة نسخة بـ user
            if (input.getAttribute('capture') === 'environment') {
                const userCameraInput = input.cloneNode(true);
                userCameraInput.setAttribute('capture', 'user');
                input.parentElement.insertBefore(userCameraInput, input.nextSibling);
                
                userCameraInput.addEventListener('change', function() {
                    if (this.files.length > 0) {
                        handleImageUpload(this);
                    }
                });
            }
        });
    }
    
    /**
     * التحقق من دعم الكاميرا
     */
    function checkCameraSupport() {
        const hasCamera = navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
        console.log('📹 Camera support:', hasCamera ? '✅ Yes' : '❌ No');
        
        if (!hasCamera) {
            console.warn('⚠️ Camera not supported on this device/browser');
            // يمكن إخفاء زر الكاميرا أو تعطيله
            document.querySelectorAll(".image-camera-btn").forEach(btn => {
                btn.disabled = false; // نبقيه مفعّل لأن input capture قد يعمل حتى بدون MediaDevices API
            });
        }
    }
    
    /**
     * تحسينات خاصة لهواتف Huawei
     */
    function applyHuaweiOptimizations() {
        if (!isHuawei) return;
        
        console.log('🔧 Applying Huawei device optimizations...');
        
        // على Huawei، قد نحتاج إلى نسخ محسّنة
        document.querySelectorAll(".image-camera-input").forEach(input => {
            // إضافة خصائص محسّنة
            input.setAttribute('accept', 'image/*,image/jpeg,image/png,image/gif');
            input.setAttribute('autocapture', 'true');
            
            // إضافة معالج fallback تلقائي
            input.addEventListener('cancel', function() {
                console.log('📸 Environment camera cancelled, trying fallback...');
                const fallbackInput = input.closest(".image-upload-container").querySelector(".image-camera-input-fallback");
                if (fallbackInput) {
                    setTimeout(() => fallbackInput.click(), 100);
                }
            }, { once: false });
        });
        
        // معالجة خاصة للـ fallback input على Huawei
        document.querySelectorAll(".image-camera-input-fallback").forEach(fallbackInput => {
            fallbackInput.setAttribute('accept', 'image/*,image/jpeg,image/png,image/gif');
            fallbackInput.addEventListener('change', function(e) {
                if (this.files.length > 0) {
                    console.log('✅ Fallback camera captured image successfully');
                    const imageInput = this.closest(".image-upload-container").querySelector(".image-input");
                    if (imageInput && window.handleImageUpload) {
                        const dataTransfer = new DataTransfer();
                        for (let file of imageInput.files) {
                            dataTransfer.items.add(file);
                        }
                        for (let file of this.files) {
                            dataTransfer.items.add(file);
                        }
                        imageInput.files = dataTransfer.files;
                        window.handleImageUpload(imageInput);
                    }
                }
            });
        });
    }
    
    /**
     * تحسينات خاصة لأجهزة Android
     */
    function applyAndroidOptimizations() {
        if (!isAndroid) return;
        
        console.log('🔧 Applying Android device optimizations...');
        
        // على Android، تأكد من قبول جميع صيغ الصور
        document.querySelectorAll("input[type='file'][accept*='image']").forEach(input => {
            input.setAttribute('accept', 'image/*');
        });
    }
    
    /**
     * إنشاء أزرار بديلة للتقاط الصور
     */
    function createFallbackButtons() {
        // يمكن إضافة أزرار بديلة هنا إذا لزم الأمر
        console.log('✅ Fallback buttons ready if needed');
    }
    
    /**
     * معالج تحميل الصور المحسّنة
     */
    window.handleImageUploadImproved = function(input) {
        try {
            const preview = input.closest(".image-upload-container")?.parentElement?.querySelector(".image-preview");
            if (!preview) return;
            
            preview.innerHTML = "";
            [...input.files].forEach((file, index) => {
                if (!file.type.startsWith("image/")) {
                    console.warn(`⚠️ Skipping non-image file: ${file.name}`);
                    return;
                }
                
                const img = document.createElement("img");
                img.src = URL.createObjectURL(file);
                img.alt = file.name;
                img.className = "preview-img";
                
                const imgItem = document.createElement("div");
                imgItem.className = "image-item";
                imgItem.dataset.index = index;
                
                const deleteBtn = document.createElement("button");
                deleteBtn.type = "button";
                deleteBtn.className = "img-delete-btn";
                deleteBtn.title = "حذف الصورة";
                deleteBtn.innerHTML = '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6M10 11v6M14 11v6"/></svg>';
                deleteBtn.addEventListener("click", function(e) {
                    e.preventDefault();
                    removeImageFile(input, index);
                });
                
                img.onload = () => {
                    console.log(`✅ Image loaded: ${file.name}`);
                    URL.revokeObjectURL(img.src);
                };
                
                img.onerror = () => {
                    console.error(`❌ Image failed to load: ${file.name}`);
                };
                
                imgItem.appendChild(img);
                imgItem.appendChild(deleteBtn);
                preview.appendChild(imgItem);
            });
            
            console.log(`✅ Loaded ${[...input.files].filter(f => f.type.startsWith("image/")).length} images`);
        } catch (error) {
            console.error('❌ Error in handleImageUploadImproved:', error);
            showCameraError('حدث خطأ في معالجة الصور.');
        }
    };
    
    /**
     * حذف صورة محسّن
     */
    window.removeImageFileImproved = function(input, index) {
        try {
            const dataTransfer = new DataTransfer();
            const files = input.files;
            
            for (let i = 0; i < files.length; i++) {
                if (i !== index) {
                    dataTransfer.items.add(files[i]);
                }
            }
            
            input.files = dataTransfer.files;
            handleImageUploadImproved(input);
            console.log(`✅ Image removed, ${input.files.length} remaining`);
        } catch (error) {
            console.error('❌ Error removing image:', error);
        }
    };
    
    /**
     * تهيئة جميع المعالجات
     */
    function initialize() {
        console.log('🚀 Initializing Camera Handler...');
        
        // انتظر قليلاً للتأكد من تحميل DOM بالكامل
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setupAll();
            });
        } else {
            setupAll();
        }
    }
    
    function setupAll() {
        checkCameraSupport();
        setupCameraHandlers();
        applyHuaweiOptimizations();
        applyAndroidOptimizations();
        createFallbackButtons();
        console.log('✅ Camera Handler initialized successfully');
    }
    
    // ابدأ التهيئة
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
