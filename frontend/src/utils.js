export const emotionColors = {
  fear: 'bg-red-500',
  anxiety: 'bg-orange-500',
  excitement: 'bg-yellow-500',
  confidence: 'bg-green-500',
  frustration: 'bg-purple-500',
  confusion: 'bg-blue-500',
  neutral: 'bg-gray-500',
};

export const emotionLabels = {
  fear: '😰 Fear',
  anxiety: '😟 Anxiety',
  excitement: '🤩 Excitement',
  confidence: '😊 Confidence',
  frustration: '😤 Frustration',
  confusion: '😕 Confusion',
  neutral: '😐 Neutral',
};

export const intentLabels = {
  budgeting: '📊 Budgeting',
  investing: '📈 Investing',
  saving: '💰 Saving',
  debt_management: '💳 Debt',
  financial_planning: '🎯 Planning',
  emotional_support: '💚 Support',
  general: '💬 General',
};

export const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};
