import { useParams } from "wouter";
import { useGetDocument, getGetDocumentQueryKey, useDeleteDocument, useReviewDocument } from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useLocation } from "wouter";
import { Loader2 } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

export default function DocumentDetail() {
  const { id } = useParams<{ id: string }>();
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const { t } = useLanguage();

  const { data: doc, isLoading } = useGetDocument(id, {
    query: { enabled: !!id, queryKey: getGetDocumentQueryKey(id) }
  });

  const deleteMutation = useDeleteDocument();
  const reviewMutation = useReviewDocument();

  const handleDelete = async () => {
    if (!confirm(t.doc_detail_delete_confirm)) return;
    try {
      await deleteMutation.mutateAsync({ id });
      toast({ title: t.doc_detail_deleted });
      setLocation("/documents");
    } catch {
      toast({ title: t.doc_detail_delete_error, variant: "destructive" });
    }
  };

  const handleReview = async () => {
    try {
      const res = await reviewMutation.mutateAsync({ id });
      toast({ title: t.doc_detail_review_done });
      setLocation(`/reviews/${res.id}`);
    } catch {
      toast({ title: t.doc_detail_review_error, variant: "destructive" });
    }
  };

  if (isLoading) {
    return <div className="flex p-8 justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  }

  if (!doc) {
    return <div>{t.doc_detail_not_found}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{doc.title}</h1>
          <p className="text-muted-foreground mt-1">
            {doc.doc_type.toUpperCase()} • {doc.project_name || t.doc_detail_no_project} • {new Date(doc.created_at).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleReview}
            disabled={reviewMutation.isPending}
            data-testid="button-run-review"
          >
            {reviewMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {t.doc_detail_run_review}
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            data-testid="button-delete-document"
          >
            {t.doc_detail_delete}
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t.doc_detail_content}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="whitespace-pre-wrap font-mono text-sm bg-muted/50 p-4 rounded-md border">
            {doc.text}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
