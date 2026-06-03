import { useState } from "react";
import { useParams } from "wouter";
import { useGetReview, getGetReviewQueryKey, exportReviewJson, exportReviewCsv } from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Download } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useLanguage } from "@/lib/i18n";

export default function ReviewDetail() {
  const { id } = useParams<{ id: string }>();
  const { t } = useLanguage();
  const [exportingJson, setExportingJson] = useState(false);
  const [exportingCsv, setExportingCsv] = useState(false);

  const { data: review, isLoading } = useGetReview(id, {
    query: { enabled: !!id, queryKey: getGetReviewQueryKey(id) }
  });

  const handleExportJson = async () => {
    setExportingJson(true);
    try {
      const data = await exportReviewJson(id);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `review_${id}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // silent
    } finally {
      setExportingJson(false);
    }
  };

  const handleExportCsv = async () => {
    setExportingCsv(true);
    try {
      const csv = await exportReviewCsv(id);
      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `review_${id}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // silent
    } finally {
      setExportingCsv(false);
    }
  };

  if (isLoading) return <div className="flex p-8 justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  if (!review) return <div>{t.review_detail_not_found}</div>;

  const result = review.review_json;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t.review_detail_title}</h1>
          <p className="text-muted-foreground mt-1">{t.review_detail_for_doc} {review.document_title || review.document_id}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleExportJson} disabled={exportingJson}>
            {exportingJson ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : <Download className="h-3 w-3 mr-1" />}
            {t.review_export_json}
          </Button>
          <Button variant="outline" size="sm" onClick={handleExportCsv} disabled={exportingCsv}>
            {exportingCsv ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : <Download className="h-3 w-3 mr-1" />}
            {t.review_export_csv}
          </Button>
          {review.needs_review && (
            <Badge variant="outline" className="bg-yellow-50 text-yellow-800 border-yellow-600/20 text-sm">
              {t.needs_review_badge}
            </Badge>
          )}
          <Badge variant="outline" className={`text-sm ${
            review.confidence === 'high' ? 'bg-green-50 text-green-700 border-green-600/20' :
            review.confidence === 'medium' ? 'bg-yellow-50 text-yellow-800 border-yellow-600/20' :
            'bg-red-50 text-red-700 border-red-600/10'
          }`}>
            {t.review_detail_confidence} {review.confidence.toUpperCase()}
          </Badge>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="md:col-span-2">
          <CardHeader><CardTitle>{t.review_detail_summary}</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed">{result.summary}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>{t.review_detail_risks}</CardTitle></CardHeader>
          <CardContent>
            {result.risks && result.risks.length > 0 ? (
              <ul className="space-y-3">
                {result.risks.map((risk, i) => (
                  <li key={i} className="flex gap-2 text-sm border-b pb-2 last:border-0">
                    <Badge variant="outline" className={`shrink-0 ${
                      risk.severity === 'high' ? 'bg-red-50 text-red-700 border-red-600/10' :
                      risk.severity === 'medium' ? 'bg-yellow-50 text-yellow-800 border-yellow-600/20' :
                      'bg-green-50 text-green-700 border-green-600/20'
                    }`}>
                      {risk.severity}
                    </Badge>
                    <span>{risk.description}</span>
                  </li>
                ))}
              </ul>
            ) : <p className="text-sm text-muted-foreground">{t.review_detail_no_risks}</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>{t.review_detail_missing_req}</CardTitle></CardHeader>
          <CardContent>
            {result.missing_requirements && result.missing_requirements.length > 0 ? (
              <ul className="list-disc pl-5 space-y-1 text-sm">
                {result.missing_requirements.map((req, i) => <li key={i}>{req}</li>)}
              </ul>
            ) : <p className="text-sm text-muted-foreground">{t.review_detail_no_req}</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>{t.review_detail_questions}</CardTitle></CardHeader>
          <CardContent>
            {result.questions_to_client && result.questions_to_client.length > 0 ? (
              <ul className="list-decimal pl-5 space-y-2 text-sm font-medium">
                {result.questions_to_client.map((q, i) => <li key={i}>{q}</li>)}
              </ul>
            ) : <p className="text-sm text-muted-foreground">{t.review_detail_no_questions}</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>{t.review_detail_criteria}</CardTitle></CardHeader>
          <CardContent>
            {result.acceptance_criteria && result.acceptance_criteria.length > 0 ? (
              <ul className="list-disc pl-5 space-y-1 text-sm">
                {result.acceptance_criteria.map((ac, i) => <li key={i}>{ac}</li>)}
              </ul>
            ) : <p className="text-sm text-muted-foreground">{t.review_detail_no_criteria}</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
