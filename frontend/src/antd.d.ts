import 'antd';

// Custom tokens using module augmentation for Ant Designs internal AliasToken interface
declare module 'antd/es/theme/internal' {
    // List of custom style properties
    interface AliasToken {
      cardBg: string;
      linkHover: string;
      gridColor: string;
  }
}