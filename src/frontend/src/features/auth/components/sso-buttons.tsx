import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';
import { FaGoogle, FaMicrosoft } from 'react-icons/fa'; // Assuming react-icons is installed

export const SSOButtons = () => {
  const { t } = useTranslation();

  const handleSSO = (provider: 'google' | 'azure_ad') => {
    // Redirect to backend endpoint that initiates OAuth flow
    window.location.href = `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/auth/sso/init?provider=${provider}`;
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      <Button variant="outline" onClick={() => handleSSO('google')}>
        <FaGoogle className="mr-2 h-4 w-4" />
        Google
      </Button>
      <Button variant="outline" onClick={() => handleSSO('azure_ad')}>
        <FaMicrosoft className="mr-2 h-4 w-4" />
        Microsoft
      </Button>
    </div>
  );
};
