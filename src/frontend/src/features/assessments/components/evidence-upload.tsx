import { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Upload, X, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useUploadEvidence } from '../api/assessments.api';
import { Evidence } from '../types/assessment.types';

interface EvidenceUploadProps {
  responseId: string;
  existingEvidence?: Evidence[];
  readOnly?: boolean;
}

export const EvidenceUpload = ({ responseId, existingEvidence = [], readOnly }: EvidenceUploadProps) => {
  const { t } = useTranslation();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { mutate: upload, isPending } = useUploadEvidence();
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadProgress(10); // Simulation start
      upload({ responseId, file }, {
        onSuccess: () => {
          setUploadProgress(100);
          setTimeout(() => setUploadProgress(0), 1000);
          if (fileInputRef.current) fileInputRef.current.value = '';
        },
        onError: () => {
          setUploadProgress(0);
          // Show toast error
        }
      });
    }
  };

  return (
    <div className="space-y-4">
      {/* List Existing */}
      <div className="space-y-2">
        {existingEvidence.map((file) => (
          <div key={file.id} className="flex items-center justify-between p-2 border rounded-md bg-muted/20">
            <div className="flex items-center gap-2 overflow-hidden">
               <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
               <a href={file.fileUrl} target="_blank" rel="noreferrer" className="text-sm truncate hover:underline text-blue-600">
                 {file.fileName}
               </a>
            </div>
            {!readOnly && (
                <Button variant="ghost" size="icon" className="h-6 w-6 text-red-500 hover:text-red-600 hover:bg-red-50">
                  <X className="h-3 w-3" />
                </Button>
            )}
          </div>
        ))}
      </div>

      {/* Upload Handler */}
      {!readOnly && (
        <div className="flex items-center gap-2">
           <input 
             type="file" 
             className="hidden" 
             ref={fileInputRef}
             onChange={handleFileChange}
             disabled={isPending}
           />
           <Button 
             variant="outline" 
             size="sm" 
             onClick={() => fileInputRef.current?.click()}
             disabled={isPending}
            >
             <Upload className="h-4 w-4 mr-2" />
             {isPending ? t('assessments.uploading') : t('assessments.uploadEvidence')}
           </Button>
           {isPending && <Progress value={uploadProgress} className="w-24 h-2" />}
        </div>
      )}
    </div>
  );
};
