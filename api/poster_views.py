import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .gemini_service import analyze_poster, analyze_poster_with_custom_prompt

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_poster_view(request):
    """
    海报分析API

    接收上传的海报图片，使用Gemini模型进行分析

    参数:
        - image: 海报图片文件（必需）
        - custom_prompt: 自定义分析提示词（可选）

    返回:
        {
            "success": true,
            "analysis": "分析结果文本",
            "message": "分析完成"
        }
    """
    try:
        logger.info(f"📤 收到海报分析请求，用户: {request.user.username}")

        # 检查是否上传了图片
        if 'image' not in request.FILES:
            logger.warning("⚠️  请求中没有图片文件")
            return Response({
                'success': False,
                'error': '请上传海报图片'
            }, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']
        logger.info(f"📷 图片信息 - 文件名: {image_file.name}, 大小: {image_file.size} 字节, 类型: {image_file.content_type}")

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
        if image_file.content_type not in allowed_types:
            logger.warning(f"⚠️  不支持的文件类型: {image_file.content_type}")
            return Response({
                'success': False,
                'error': f'不支持的文件类型，请上传图片文件 (jpg, png, webp, gif)'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件大小（限制10MB）
        max_size = 10 * 1024 * 1024  # 10MB
        if image_file.size > max_size:
            logger.warning(f"⚠️  文件过大: {image_file.size} 字节")
            return Response({
                'success': False,
                'error': '图片文件过大，请上传小于10MB的图片'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取自定义提示词（如果有）
        custom_prompt = request.data.get('custom_prompt', None)

        # 调用Gemini服务进行分析
        if custom_prompt:
            logger.info(f"🤖 使用自定义提示词进行分析...")
            result = analyze_poster_with_custom_prompt(image_file, custom_prompt)
        else:
            logger.info(f"🤖 使用默认提示词进行分析...")
            result = analyze_poster(image_file)

        # 检查分析结果
        if not result['success']:
            logger.error(f"❌ 分析失败: {result.get('error', '未知错误')}")
            return Response({
                'success': False,
                'error': result.get('error', '分析失败')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"✅ 海报分析完成，结果长度: {len(result['analysis'])} 字符")

        return Response({
            'success': True,
            'analysis': result['analysis'],
            'message': '海报分析完成'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"❌ 海报分析时发生异常: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analysis_templates(request):
    """
    获取预设的分析模板

    返回一些常用的分析提示词模板供用户选择
    """
    templates = [
        {
            'id': 1,
            'name': '产品分析',
            'description': '深度理解海报传达的产品信息和价值',
            'prompt': '请仔细分析这张海报，写出你对这张海报的理解：\n\n1. **产品定位**：这是什么产品/服务？面向什么人群？\n2. **核心价值**：产品的主要卖点和独特优势是什么？\n3. **信息传达**：海报想要传达的核心信息是什么？\n4. **情感共鸣**：海报营造了什么氛围和情感？\n5. **品牌印象**：给人留下什么样的品牌印象？\n\n请用中文详细说明你的理解，语言通俗易懂。'
        },
        {
            'id': 2,
            'name': '客户视角分析',
            'description': '站在客户角度分析吸引力和可能的疑问',
            'prompt': '请从客户的角度分析这张海报：\n\n## 一、吸引力分析\n如果你是目标客户，这个产品哪些地方最吸引你？请列举3-5个具体的吸引点。\n\n## 二、客户疑问\n客户看到这张海报后，可能会问出什么问题？请列举5-8个最可能的问题。\n\n## 三、专业答复\n针对上述每个问题，从专业角度给出令客户满意的答复。答复要点：\n- 解答要准确、专业\n- 语言要通俗易懂\n- 要能打消客户顾虑\n- 突出产品优势和价值\n\n请详细展开说明。'
        },
        {
            'id': 3,
            'name': '朋友圈文案',
            'description': '基于海报内容生成多角度的朋友圈营销文案',
            'prompt': '根据这张海报，写出不同切入角度的朋友圈文案。每个文案要求：\n\n**文案要求**：\n- 字数控制在100-200字\n- 语言生动、有感染力\n- 要有明确的行动召唤\n- 适合不同场景使用\n\n**请提供以下5种角度的文案**：\n\n1. **痛点切入型**：从客户痛点出发，引起共鸣\n2. **利益驱动型**：突出产品利益和优势\n3. **故事叙述型**：用小故事或场景引入\n4. **数据说话型**：用具体数据和案例说服\n5. **情感共鸣型**：营造情感氛围，引发情感共鸣\n\n每个文案要包含合适的emoji表情，并在文末添加适当的话题标签。'
        },
        {
            'id': 4,
            'name': '全面分析',
            'description': '对海报进行全方位的设计、内容和营销分析',
            'prompt': '请仔细分析这张海报/宣传图，提供以下内容的详细分析：\n\n1. 视觉设计分析：整体风格、色彩搭配、排版布局\n2. 内容解读：识别文字内容、核心信息、目标受众\n3. 营销要素：主要卖点、情感诉求、行动召唤\n4. 改进建议：设计优化、内容改进、提高转化率\n\n请用中文回答，结构清晰，分点说明。'
        },
        {
            'id': 5,
            'name': '文案提取',
            'description': '识别并提取海报中的所有文字内容',
            'prompt': '请识别并提取这张海报中的所有文字内容，包括：\n1. 标题文案\n2. 副标题文案\n3. 正文内容\n4. 小字说明\n5. 按钮文字\n\n请按从上到下、从左到右的顺序整理，用中文输出。'
        },
        {
            'id': 6,
            'name': '设计分析',
            'description': '专注于海报的视觉设计分析',
            'prompt': '请从专业设计师的角度分析这张海报的设计：\n1. 配色方案和色彩心理学\n2. 排版布局和视觉层次\n3. 字体选择和字号搭配\n4. 图片元素和留白运用\n5. 整体风格定位\n\n请提供详细的设计分析。'
        },
        {
            'id': 7,
            'name': '营销效果评估',
            'description': '评估海报的营销效果和转化潜力',
            'prompt': '请从营销角度评估这张海报：\n1. 目标受众定位是否清晰\n2. 核心卖点是否突出\n3. 视觉吸引力评分（1-10分）\n4. 行动召唤是否明确\n5. 可能的转化率和改进建议\n\n请提供具体的营销分析和优化建议。'
        },
        {
            'id': 8,
            'name': '竞品对比',
            'description': '分析海报相对于行业标准的优劣势',
            'prompt': '请将这张海报与同行业标准进行对比分析：\n1. 相比行业常见设计的优势\n2. 存在的不足和短板\n3. 创新点和亮点\n4. 可借鉴的改进方向\n5. 在竞品中的竞争力评估\n\n请提供客观的对比分析。'
        }
    ]

    return Response({
        'success': True,
        'templates': templates
    }, status=status.HTTP_200_OK)
