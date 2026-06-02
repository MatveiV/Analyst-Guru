import { useParams } from "wouter";
import { useGetDocument, getGetDocumentQueryKey, useDeleteDocument, useReviewDocument } from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useLocation } from "wouter";
import { Loader2 } from "lucide-react";

export default function DocumentDetail() {
  const { id } = useParams<{ id: string }>();
  const [, setLocation] = useLocation();
  const { toast } = useToast();

  const { data: doc, isLoading } = useGetDocument(id, {
    query: {
      enabled: !!id,
      queryKey: getGetDocumentQueryKey(id),
    }
  });

  const deleteMutation = useDeleteDocument();
  const reviewMutation = useReviewDocument();

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this document?")) return;
    try {
      await deleteMutation.mutateAsync({ id });
      toast({ title: "Document deleted" });
      setLocation("/documents");
    } catch (e) {
      toast({ title: "Failed to delete", variant: "destructive" });
    }
  };

  const handleReview = async () => {
    try {
      const res = await reviewMutation.mutateAsync({ id });
      toast({ title: "Review completed" });
      setLocation(`/reviews/${res.id}`);
    } catch (e) {
      toast({ title: "Review failed", variant: "destructive" });
    }
  };

  if (isLoading) {
    return <div className="flex p-8 justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  }

  if (!doc) {
    return <div>Document not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{doc.title}</h1>
          <p className="text-muted-foreground mt-1">
            {doc.doc_type.toUpperCase()} • {doc.project_name || "No Project"} • {new Date(doc.created_at).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleReview} disabled={reviewMutation.isPending}>
            {reviewMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Run AI Review
          </Button>
          <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
            Delete
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Content</CardTitle>
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
