import { useParams } from "wouter";
import { useGetReview, getGetReviewQueryKey } from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function ReviewDetail() {
  const { id } = useParams<{ id: string }>();

  const { data: review, isLoading } = useGetReview(id, {
    query: {
      enabled: !!id,
      queryKey: getGetReviewQueryKey(id),
    }
  });

  if (isLoading) return <div className="flex p-8 justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  if (!review) return <div>Review not found</div>;

  const result = review.review_json;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Review Details</h1>
          <p className="text-muted-foreground mt-1">For document: {review.document_title || review.document_id}</p>
        </div>
        <div className="flex items-center gap-2">
          {review.needs_review && (
            <Badge variant="outline" className="bg-yellow-50 text-yellow-800 border-yellow-600/20 text-sm">
              ⚠️ Требует проверки
            </Badge>
          )}
          <Badge variant="outline" className={`text-sm ${
            review.confidence === 'high' ? 'bg-green-50 text-green-700 border-green-600/20' :
            review.confidence === 'medium' ? 'bg-yellow-50 text-yellow-800 border-yellow-600/20' :
            'bg-red-50 text-red-700 border-red-600/10'
          }`}>
            Confidence: {review.confidence.toUpperCase()}
          </Badge>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed">{result.summary}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Identified Risks</CardTitle>
          </CardHeader>
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
            ) : <p className="text-sm text-muted-foreground">No risks identified.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Missing Requirements</CardTitle>
          </CardHeader>
          <CardContent>
            {result.missing_requirements && result.missing_requirements.length > 0 ? (
              <ul className="list-disc pl-5 space-y-1 text-sm">
                {result.missing_requirements.map((req, i) => (
                  <li key={i}>{req}</li>
                ))}
              </ul>
            ) : <p className="text-sm text-muted-foreground">None found.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Questions to Client</CardTitle>
          </CardHeader>
          <CardContent>
            {result.questions_to_client && result.questions_to_client.length > 0 ? (
              <ul className="list-decimal pl-5 space-y-2 text-sm font-medium">
                {result.questions_to_client.map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
            ) : <p className="text-sm text-muted-foreground">No questions generated.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Acceptance Criteria</CardTitle>
          </CardHeader>
          <CardContent>
            {result.acceptance_criteria && result.acceptance_criteria.length > 0 ? (
              <ul className="list-disc pl-5 space-y-1 text-sm">
                {result.acceptance_criteria.map((ac, i) => (
                  <li key={i}>{ac}</li>
                ))}
              </ul>
            ) : <p className="text-sm text-muted-foreground">Not specified.</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
