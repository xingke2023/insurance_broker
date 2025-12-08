import { API_BASE_URL } from '../config';

/**
 * Gemini API 服务
 * 统一管理所有与 Gemini 图像生成相关的 API 调用
 */

// ==================== IP 形象生成 API ====================

/**
 * 生成 IP 形象 (V1 版本 - 旧接口)
 * @deprecated 建议使用 generateIPImageV2
 * @param {File} image - 上传的照片文件
 * @param {string} prompt - 提示语描述
 * @returns {Promise<{status: string, image_url?: string, message?: string}>}
 */
export const generateIPImageV1 = async (image, prompt) => {
  try {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('prompt', prompt);

    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/ip-image/generate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData,
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('生成IP形象失败 (V1):', error);
    throw error;
  }
};

/**
 * 生成 IP 形象 (V2 版本 - 推荐使用)
 * 支持自定义纵横比，提供更好的图像质量
 * @param {File} image - 上传的照片文件
 * @param {string} prompt - 提示语描述
 * @param {string} aspectRatio - 纵横比 (例如: '1:1', '16:9', '9:16')
 * @returns {Promise<{status: string, image_url?: string, message?: string}>}
 */
export const generateIPImageV2 = async (image, prompt, aspectRatio = '1:1') => {
  try {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('prompt', prompt);
    formData.append('aspect_ratio', aspectRatio);

    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/ip-image/generate-v2`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData,
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('生成IP形象失败 (V2):', error);
    throw error;
  }
};

/**
 * 生成 IP 形象 (默认使用 V2)
 * @param {File} image - 上传的照片文件
 * @param {string} prompt - 提示语描述
 * @param {string} aspectRatio - 纵横比 (例如: '1:1', '16:9', '9:16')
 * @returns {Promise<{status: string, image_url?: string, message?: string}>}
 */
export const generateIPImage = generateIPImageV2;

// ==================== 文案配图生成 API ====================

/**
 * 生成文案配图 (V1 版本 - 旧接口)
 * @deprecated 建议使用 generateContentImageV2
 * @param {string} content - 文案内容
 * @param {number} imageIndex - 图片索引（用于生成多张图片时）
 * @param {Object} options - 可选参数
 * @param {boolean} options.includeIpImage - 是否包含IP形象
 * @param {string} options.ipImageUrl - IP形象的URL
 * @param {string} aspectRatio - 纵横比 (例如: '1:1', '16:9', '9:16')
 * @returns {Promise<{status: string, image_url?: string, message?: string}>}
 */
export const generateContentImageV1 = async (content, imageIndex = 1, options = {}, aspectRatio = '1:1') => {
  try {
    const formData = new FormData();
    formData.append('content', content);
    formData.append('image_index', imageIndex);
    formData.append('aspect_ratio', aspectRatio);

    // 如果勾选包含IP形象且有IP形象，则添加IP形象URL
    if (options.includeIpImage && options.ipImageUrl) {
      formData.append('include_ip_image', 'true');
      formData.append('ip_image_url', options.ipImageUrl);
    }

    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/ip-image/generate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData,
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('生成文案配图失败 (V1):', error);
    throw error;
  }
};

/**
 * 生成文案配图 (V2 版本 - 推荐使用)
 * 提供更好的图像质量和优化的提示词处理
 * @param {string} content - 文案内容
 * @param {number} imageIndex - 图片索引（用于生成多张图片时）
 * @param {Object} options - 可选参数
 * @param {boolean} options.includeIpImage - 是否包含IP形象
 * @param {string} options.ipImageUrl - IP形象的URL
 * @param {string} aspectRatio - 纵横比 (例如: '1:1', '16:9', '9:16')
 * @returns {Promise<{status: string, image_url?: string, message?: string}>}
 */
export const generateContentImageV2 = async (content, imageIndex = 1, options = {}, aspectRatio = '1:1') => {
  try {
    const formData = new FormData();
    formData.append('content', content);
    formData.append('image_index', imageIndex);
    formData.append('aspect_ratio', aspectRatio);

    // 如果勾选包含IP形象且有IP形象，则添加IP形象URL
    if (options.includeIpImage && options.ipImageUrl) {
      formData.append('include_ip_image', 'true');
      formData.append('ip_image_url', options.ipImageUrl);
    }

    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/ip-image/generate-v2`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData,
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('生成文案配图失败 (V2):', error);
    throw error;
  }
};

/**
 * 生成文案配图 (默认使用 V2)
 * @param {string} content - 文案内容
 * @param {number} imageIndex - 图片索引（用于生成多张图片时）
 * @param {Object} options - 可选参数
 * @param {boolean} options.includeIpImage - 是否包含IP形象
 * @param {string} options.ipImageUrl - IP形象的URL
 * @param {string} aspectRatio - 纵横比 (例如: '1:1', '16:9', '9:16')
 * @returns {Promise<{status: string, image_url?: string, message?: string}>}
 */
export const generateContentImage = generateContentImageV2;

// ==================== IP 形象管理 API ====================

/**
 * 获取已保存的 IP 形象
 * @returns {Promise<{status: string, has_saved: boolean, data?: Object}>}
 */
export const getSavedIPImage = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/ip-image/saved`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('获取已保存的IP形象失败:', error);
    throw error;
  }
};

/**
 * 保存 IP 形象
 * @param {string} imageUrl - 生成的图片URL
 * @param {string} prompt - 提示语
 * @returns {Promise<{status: string, message?: string}>}
 */
export const saveIPImage = async (imageUrl, prompt) => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/ip-image/save`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        generated_image_url: imageUrl,
        prompt: prompt
      })
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('保存IP形象失败:', error);
    throw error;
  }
};

// ==================== 使用统计 API ====================

/**
 * 获取使用统计信息
 * @param {string} type - 统计类型 ('ip_image' 或 'content_image')
 * @returns {Promise<{status: string, data?: Object}>}
 */
export const getUsageStats = async (type = 'ip_image') => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/api/gemini/usage-stats?type=${type}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('获取使用统计失败:', error);
    throw error;
  }
};
