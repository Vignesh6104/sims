import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('default');

  useEffect(() => {
    // Apply the theme to the HTML element (root)
    const root = window.document.documentElement;
    
    if (theme === 'default') {
      root.removeAttribute('data-theme');
    } else {
      root.setAttribute('data-theme', theme);
    }
    
    console.log(`Active Theme: ${theme}`);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => {
      if (prev === 'default') return 'beige';
      if (prev === 'beige') return 'royal';
      if (prev === 'royal') return 'forest';
      if (prev === 'forest') return 'purple';
      if (prev === 'purple') return 'nordic';
      if (prev === 'nordic') return 'midnight';
      return 'default';
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
