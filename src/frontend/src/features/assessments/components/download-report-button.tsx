import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { useState } from "react";
import { api } from "@/lib/api";
import { useTranslation } from "react-i18next";

interface DownloadReportButtonProps {
  assessmentId: string;
  className?: string;
  disabled?: boolean;
}

export function DownloadReportButton({ assessmentId, className, disabled }: DownloadReportButtonProps) {
  const { t } = useTranslation();
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const response = await api.get(`/reports/assessments/${assessmentId}/pdf`, {
        responseType: 'blob', // Important for binary data
      });

      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Try to get filename from content-disposition or default
      const filename = `assessment_report_${assessmentId}.pdf`;
      link.setAttribute('download', filename);
      
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download report", error);
      // Ideally show a toast notification here
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <Button 
      variant="outline" 
      size="sm" 
      className={className} 
      onClick={handleDownload}
      disabled={disabled || isDownloading}
    >
      <Download className="mr-2 h-4 w-4" />
      {isDownloading ? t('reports.generating') : t('reports.download')}
    </Button>
  );
}
