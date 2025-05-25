export const roundDecimal = (num, decimalPlaces) => {
  try {
    const roundedStr = num.toFixed(decimalPlaces)
    return Number(roundedStr) === 0 ? (0).toFixed(decimalPlaces) : roundedStr;
  } catch (e) { // case where num is not a number 
    return "N/A";
  }
}

export const formatDate = (dateString) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}