# config/transitions.py - 叙事转场配置
# 电影级别的过场文本，营造沉浸式体验

TRANSITION_TEXTS = {
    "1_to_2": {
        "text": "⏳ 现实的冰水，即将浇下...",
        "subtitle": "第二幕：现实击穿",
        "duration": 2.5
    },
    "2_to_3": {
        "text": "🔨 击碎旧地图，是为了绘制新大陆...",
        "subtitle": "第三幕：认知重构", 
        "duration": 2.5
    },
    "3_to_4": {
        "text": "⚡ 理论已成，开始铸造你的武器...",
        "subtitle": "第四幕：智慧武装",
        "duration": 2.5
    }
}

# 转场样式配置
TRANSITION_STYLE = """
<style>
.transition-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 60vh;
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem 0;
    color: white;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.transition-main-text {
    font-size: 2.2rem;
    font-weight: 600;
    margin-bottom: 1rem;
    opacity: 0;
    animation: fadeInUp 1s ease-out forwards;
}

.transition-subtitle {
    font-size: 1.2rem;
    opacity: 0.8;
    margin-bottom: 2rem;
    opacity: 0;
    animation: fadeInUp 1s ease-out 0.5s forwards;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.loading-dots {
    display: inline-block;
    position: relative;
    width: 80px;
    height: 80px;
    margin-top: 2rem;
}

.loading-dots div {
    position: absolute;
    top: 33px;
    width: 13px;
    height: 13px;
    border-radius: 50%;
    background: white;
    animation-timing-function: cubic-bezier(0, 1, 1, 0);
}

.loading-dots div:nth-child(1) {
    left: 8px;
    animation: loading1 0.6s infinite;
}

.loading-dots div:nth-child(2) {
    left: 8px;
    animation: loading2 0.6s infinite;
}

.loading-dots div:nth-child(3) {
    left: 32px;
    animation: loading2 0.6s infinite;
}

.loading-dots div:nth-child(4) {
    left: 56px;
    animation: loading3 0.6s infinite;
}

@keyframes loading1 {
    0% { transform: scale(0); }
    100% { transform: scale(1); }
}

@keyframes loading3 {
    0% { transform: scale(1); }
    100% { transform: scale(0); }
}

@keyframes loading2 {
    0% { transform: translate(0, 0); }
    100% { transform: translate(24px, 0); }
}
</style>
"""
