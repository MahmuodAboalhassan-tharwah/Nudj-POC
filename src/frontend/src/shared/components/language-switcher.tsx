import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Languages } from 'lucide-react';

export const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'ar' : 'en';
    i18n.changeLanguage(newLang);
  };

  return (
    <Button 
      variant="ghost" 
      size="sm" 
      onClick={toggleLanguage}
      className="gap-2 text-muted-foreground hover:text-primary transition-colors"
      title={i18n.language === 'en' ? 'Switch to Arabic' : 'التغيير للغة الإنجليزية'}
    >
      <Languages className="h-4 w-4" />
      <span className="text-xs font-medium uppercase">
        {i18n.language === 'en' ? 'AR' : 'EN'}
      </span>
    </Button>
  );
};
