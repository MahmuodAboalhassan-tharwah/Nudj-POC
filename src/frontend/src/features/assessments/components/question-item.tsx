import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { AssessmentElementResponse } from '../types/assessment.types';
import { useSubmitResponse } from '../api/assessments.api';
import { MaturitySelector } from './maturity-selector';
import { EvidenceUpload } from './evidence-upload';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Save, MessageSquare } from 'lucide-react';
import { CommentThread } from '../../comments/components/comment-thread';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface QuestionItemProps {
  elementId: number; // Framework ID
  response?: AssessmentElementResponse;
  domainId: string; // Database Record ID
  readOnly?: boolean;
}

export const QuestionItem = ({ elementId, response, domainId, readOnly }: QuestionItemProps) => {
  const { t } = useTranslation();
  // Local state for optimistic UI / debouncing
  const [level, setLevel] = useState<number | null>(response?.maturityLevel || null);
  const [comment, setComment] = useState(response?.comment || '');
  const [isDirty, setIsDirty] = useState(false);
  
  const { mutate: submit, isPending } = useSubmitResponse();
  
  useEffect(() => {
    setLevel(response?.maturityLevel || null);
    setComment(response?.comment || '');
    setIsDirty(false);
  }, [response]);

  const handleSave = () => {
    if (!response) return; // Should create response first? Or assume implementation details...
    // Actually, backend creates empty responses on assessment creation.
    
    if (level === null) return;

    submit({
       responseId: response.id,
       data: { 
         elementId, // Redundant but mostly for validation
         maturityLevel: level,
         comment 
       }
    }, {
      onSuccess: () => setIsDirty(false)
    });
  };

  return (
    <Card className="mb-6 border-l-4 border-l-primary/30 transition-all duration-300 hover:shadow-md hover:border-l-primary shadow-sm bg-white/50 backdrop-blur-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-bold tracking-tight text-slate-800">{t('assessments.element')} {elementId}</CardTitle>
          <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground bg-slate-100 px-2 py-1 rounded">{t('assessments.frameworkElement')}</span>
        </div>
        <p className="text-sm text-slate-500 font-medium leading-relaxed mt-1">
          {t(`assessments.elementDescriptions.${elementId}`, { defaultValue: 'Technical competency and processes related to this area of the maturity framework.' })}
        </p>
      </CardHeader>
      <CardContent className="space-y-8 pt-0">
        <Tabs defaultValue="response" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-slate-100/50 p-1 rounded-xl mb-6">
            <TabsTrigger value="response" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm text-xs font-bold uppercase tracking-wider">
              {t('assessments.findings')}
            </TabsTrigger>
            <TabsTrigger value="discussion" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm text-xs font-bold uppercase tracking-wider flex items-center gap-2">
              {t('assessments.discussion')} 
              {response?.comments && response.comments.length > 0 && (
                <span className="bg-primary text-white text-[10px] h-4 w-4 rounded-full flex items-center justify-center">
                  {response.comments.length}
                </span>
              )}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="response" className="space-y-8 mt-0 outline-none">
            {/* Maturity Selection */}
            <div className="space-y-3">
              <Label className="text-sm font-bold uppercase tracking-wider text-slate-700">{t('assessments.maturityLevel')}</Label>
              <div className="p-1 bg-slate-50 rounded-xl inline-block w-full">
                <MaturitySelector 
                  value={level} 
                  onChange={(val) => { setLevel(val); setIsDirty(true); }} 
                  disabled={readOnly || isPending}
                />
              </div>
            </div>

            {/* Evidence */}
            <div className="space-y-3">
              <Label className="text-sm font-bold uppercase tracking-wider text-slate-700">{t('assessments.evidenceDocumentation')}</Label>
              <div className="rounded-xl border border-dashed border-slate-200 p-2 transition-colors hover:border-primary/30">
                {response && (
                    <EvidenceUpload 
                      responseId={response.id} 
                      existingEvidence={response.evidence} 
                      readOnly={readOnly} 
                    />
                )}
              </div>
            </div>

            {/* Comment */}
            <div className="space-y-3">
              <Label className="text-sm font-bold uppercase tracking-wider text-slate-700">{t('assessments.analysisObservations')}</Label>
              <Textarea 
                value={comment} 
                onChange={(e) => { setComment(e.target.value); setIsDirty(true); }}
                placeholder={t('assessments.placeholderAnalysis')}
                disabled={readOnly || isPending}
                className="min-h-[120px] resize-none bg-white border-slate-200 focus:ring-primary/20 transition-all rounded-xl"
              />
            </div>

            {/* Actions */}
            {!readOnly && isDirty && (
              <div className="flex justify-end pt-2">
                <Button 
                  onClick={handleSave} 
                  disabled={isPending}
                  className="shadow-lg shadow-primary/20 transition-all hover:scale-105 active:scale-95"
                >
                  {isPending ? (
                    <div className="flex items-center gap-2">
                      <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      {t('assessments.saving')}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <Save className="h-4 w-4" />
                      {t('assessments.saveResponse')}
                    </div>
                  )}
                </Button>
              </div>
            )}
          </TabsContent>

          <TabsContent value="discussion" className="mt-0 outline-none">
            {response ? (
              <div className="bg-slate-50/50 rounded-2xl p-6 border border-slate-100">
                <div className="flex items-center gap-2 mb-6">
                  <div className="p-2 rounded-lg bg-white shadow-sm border border-slate-100">
                    <MessageSquare className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-800">{t('assessments.teamDiscussion')}</h3>
                    <p className="text-[10px] font-medium text-slate-500 uppercase tracking-widest">{t('assessments.collaborateOnFindings')}</p>
                  </div>
                </div>
                <CommentThread responseId={response.id} />
              </div>
            ) : (
              <div className="p-8 text-center text-slate-500">
                {t('assessments.saveFirstToDiscuss')}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
