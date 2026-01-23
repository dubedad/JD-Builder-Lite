const storage = {
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      if (error.code === 22 || error.code === 1014 ||
          error.name === 'QuotaExceededError' ||
          error.name === 'NS_ERROR_DOM_QUOTA_REACHED') {
        console.warn('localStorage quota exceeded, using sessionStorage fallback');
        try {
          sessionStorage.setItem(key, JSON.stringify(value));
          return true;
        } catch (e) {
          return false;
        }
      }
      return false;
    }
  },
  get(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key) || sessionStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      return defaultValue;
    }
  }
};
