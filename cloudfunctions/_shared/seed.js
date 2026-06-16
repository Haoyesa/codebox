// @created 2026-06-16 v0.1 - 12 行业 + 60+ 岗位种子数据
'use strict';

const INDUSTRIES = [
  { code: 'internet', name: '互联网', icon: '💻', sort: 1,
    companies: ['字节跳动', '腾讯', '阿里巴巴', '美团', '京东', '拼多多', '快手'],
    jobs: [
      { code: 'frontend', name: '前端工程师', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }, { code: 'lead', name: '专家' }] },
      { code: 'backend', name: '后端工程师', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }, { code: 'lead', name: '专家' }] },
      { code: 'algorithm', name: '算法工程师', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }] },
      { code: 'product', name: '产品经理', levels: [{ code: 'junior', name: '初级产品' }, { code: 'mid', name: '高级产品' }, { code: 'senior', name: '产品专家' }] },
      { code: 'operation', name: '运营', levels: [{ code: 'junior', name: '运营专员' }, { code: 'mid', name: '运营经理' }, { code: 'senior', name: '运营总监' }] },
    ]
  },
  { code: 'finance', name: '金融', icon: '🏦', sort: 2,
    companies: ['中金', '中信证券', '招商银行', '平安', '蚂蚁集团', '京东金融'],
    jobs: [
      { code: 'analyst', name: '金融分析师', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }] },
      { code: 'risk', name: '风控', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }] },
      { code: 'fintech', name: '金融科技', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }] },
    ]
  },
  { code: 'consulting', name: '咨询', icon: '💼', sort: 3,
    companies: ['麦肯锡', '波士顿咨询', '贝恩', '罗兰贝格', '德勤'],
    jobs: [
      { code: 'consultant', name: '咨询顾问', levels: [{ code: 'analyst', name: '分析师' }, { code: 'associate', name: '助理' }, { code: 'manager', name: '经理' }, { code: 'partner', name: '合伙人' }] },
    ]
  },
  { code: 'fmcg', name: '快消', icon: '🛒', sort: 4,
    companies: ['宝洁', '联合利华', '欧莱雅', '玛氏', '可口可乐'],
    jobs: [
      { code: 'brand', name: '品牌经理', levels: [{ code: 'assistant', name: '助理品牌经理' }, { code: 'manager', name: '品牌经理' }, { code: 'senior', name: '高级品牌经理' }] },
      { code: 'sales', name: '销售', levels: [{ code: 'rep', name: '销售代表' }, { code: 'manager', name: '销售经理' }] },
    ]
  },
  { code: 'manufacturing', name: '制造', icon: '🏭', sort: 5,
    companies: ['比亚迪', '宁德时代', '富士康', '海尔', '美的'],
    jobs: [
      { code: 'me', name: '机械工程师', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }] },
      { code: 'ee', name: '电气工程师', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }] },
      { code: 'ie', name: '工业工程师', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }] },
    ]
  },
  { code: 'education', name: '教育', icon: '📚', sort: 6,
    companies: ['新东方', '好未来', '猿辅导', '作业帮', '字节跳动教育'],
    jobs: [
      { code: 'teacher', name: '教师', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }] },
      { code: 'tutor', name: '课程顾问', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }] },
    ]
  },
  { code: 'medical', name: '医疗', icon: '⚕️', sort: 7,
    companies: ['恒瑞医药', '复星医药', '迈瑞医疗', '药明康德'],
    jobs: [
      { code: 'doctor', name: '医生', levels: [{ code: 'resident', name: '住院医师' }, { code: 'attending', name: '主治医师' }, { code: 'associate', name: '副主任医师' }] },
      { code: 'pharma', name: '医药代表', levels: [{ code: 'rep', name: '代表' }, { code: 'manager', name: '地区经理' }] },
    ]
  },
  { code: 'auto', name: '汽车', icon: '🚗', sort: 8,
    companies: ['比亚迪', '蔚来', '理想', '小鹏', '特斯拉中国', '上汽'],
    jobs: [
      { code: 'adas', name: '自动驾驶工程师', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }] },
      { code: 'vehicle', name: '整车工程师', levels: [{ code: 'junior', name: '初级' }, { code: 'mid', name: '中级' }, { code: 'senior', name: '高级' }] },
    ]
  },
  { code: 'realestate', name: '地产', icon: '🏢', sort: 9,
    companies: ['万科', '保利', '碧桂园', '龙湖'],
    jobs: [
      { code: 'invest', name: '投资拓展', levels: [{ code: 'manager', name: '经理' }, { code: 'senior', name: '高级经理' }] },
      { code: 'marketing', name: '营销', levels: [{ code: 'manager', name: '经理' }, { code: 'senior', name: '高级经理' }] },
    ]
  },
  { code: 'media', name: '传媒', icon: '📺', sort: 10,
    companies: ['央视', '湖南卫视', '芒果TV', '爱奇艺', '腾讯视频'],
    jobs: [
      { code: 'editor', name: '编导', levels: [{ code: 'junior', name: '助理编导' }, { code: 'mid', name: '编导' }, { code: 'senior', name: '高级编导' }] },
      { code: 'reporter', name: '记者', levels: [{ code: 'junior', name: '记者' }, { code: 'senior', name: '高级记者' }] },
    ]
  },
  { code: 'stateowned', name: '国企', icon: '🏛️', sort: 11,
    companies: ['国家电网', '中石油', '中石化', '中国移动', '中国电信'],
    jobs: [
      { code: 'admin', name: '行政管理', levels: [{ code: 'staff', name: '科员' }, { code: 'manager', name: '科长' }] },
      { code: 'tech', name: '技术岗', levels: [{ code: 'staff', name: '技术员' }, { code: 'engineer', name: '工程师' }] },
    ]
  },
  { code: 'foreign', name: '外企', icon: '🌐', sort: 12,
    companies: ['Microsoft', 'Google', 'Apple', 'Amazon', 'Meta', 'Tesla'],
    jobs: [
      { code: 'engineer', name: 'Software Engineer', levels: [{ code: 'e3', name: 'E3' }, { code: 'e4', name: 'E4' }, { code: 'e5', name: 'E5' }, { code: 'e6', name: 'E6' }] },
      { code: 'pm', name: 'Product Manager', levels: [{ code: 'pm1', name: 'PM1' }, { code: 'pm2', name: 'PM2' }, { code: 'pm3', name: 'PM3' }] },
    ]
  },
];

module.exports = { INDUSTRIES };