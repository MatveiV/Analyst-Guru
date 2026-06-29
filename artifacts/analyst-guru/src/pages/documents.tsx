import { useState } from "react";
import { useListDocuments, getListDocumentsQueryKey, useCreateDocument } from "@workspace/api-client-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Link, useLocation } from "wouter";
import { useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Brain } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useLanguage } from "@/lib/i18n";

const API_BASE = import.meta.env.BASE_URL?.replace(/\/$/, "") || "";

export default function Documents() {
  const { t } = useLanguage();
  const [page, setPage] = useState(1);
  const limit = 20;
  const offset = (page - 1) * limit;

  const { data: documents, isLoading } = useListDocuments({ limit, offset }, {
    query: { queryKey: getListDocumentsQueryKey({ limit, offset }) }
  });

  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [, setLocation] = useLocation();
  const createDocMutation = useCreateDocument();
  const [runningReviews, setRunningReviews] = useState<Set<string>>(new Set());
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [docType, setDocType] = useState("tz");
  const [projectName, setProjectName] = useState("");
  const [reasoningMode, setReasoningMode] = useState("none");

  const handleRunReview = async (docId: string) => {
    setRunningReviews(prev => new Set(prev).add(docId));
    try {
      const params = reasoningMode !== "none" ? `?reasoning_mode=${reasoningMode}` : "";
      const res = await fetch(`${API_BASE}/api/documents/${docId}/review${params}`, { method: "POST" });
      if (!res.ok) throw new Error("Review failed");
      const data = await res.json();
      toast({ title: t.doc_detail_review_done });
      setLocation(`/reviews/${data.review_id}`);
    } catch {
      toast({ title: t.doc_detail_review_error, variant: "destructive" });
    } finally {
      setRunningReviews(prev => { const next = new Set(prev); next.delete(docId); return next; });
    }
  };

  const handleCreate = async () => {
    if (!title || !text) return;
    try {
      await createDocMutation.mutateAsync({
        data: { title, text, doc_type: docType, project_name: projectName || null }
      });
      toast({ title: t.docs_created_success });
      queryClient.invalidateQueries({ queryKey: getListDocumentsQueryKey({ limit, offset }) });
      setOpen(false);
      setTitle("");
      setText("");
    } catch {
      toast({ title: t.docs_create_error, variant: "destructive" });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t.docs_title}</h1>
          <p className="text-muted-foreground">{t.docs_subtitle}</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button data-testid="button-add-document">{t.docs_add}</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>{t.docs_add_title}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>{t.docs_title_field}</Label>
                <Input
                  data-testid="input-doc-title"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  placeholder={t.docs_title_placeholder}
                />
              </div>
              <div className="space-y-2">
                <Label>{t.docs_type_field}</Label>
                <Select value={docType} onValueChange={setDocType}>
                  <SelectTrigger data-testid="select-doc-type">
                    <SelectValue placeholder={t.docs_select_type} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tz">TZ</SelectItem>
                    <SelectItem value="brd">BRD</SelectItem>
                    <SelectItem value="srs">SRS</SelectItem>
                    <SelectItem value="urs">URS</SelectItem>
                    <SelectItem value="adr">ADR</SelectItem>
                    <SelectItem value="api_spec">API Spec</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>{t.docs_project_field}</Label>
                <Input
                  data-testid="input-doc-project"
                  value={projectName}
                  onChange={e => setProjectName(e.target.value)}
                  placeholder={t.docs_project_placeholder}
                />
              </div>
              <div className="space-y-2">
                <Label>{t.docs_content_field}</Label>
                <Textarea
                  data-testid="textarea-doc-content"
                  value={text}
                  onChange={e => setText(e.target.value)}
                  placeholder={t.docs_content_placeholder}
                  className="h-40 font-mono text-sm"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setOpen(false)} data-testid="button-cancel">
                {t.docs_cancel}
              </Button>
              <Button
                onClick={handleCreate}
                disabled={createDocMutation.isPending}
                data-testid="button-save-document"
              >
                {createDocMutation.isPending ? t.docs_saving : t.docs_save}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex items-center gap-3">
        <Brain className="h-4 w-4 text-muted-foreground" />
        <Select value={reasoningMode} onValueChange={setReasoningMode}>
          <SelectTrigger className="w-[220px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">{t.reasoning_none}</SelectItem>
            <SelectItem value="cot">{t.reasoning_cot}</SelectItem>
            <SelectItem value="react">{t.reasoning_react}</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-xs text-muted-foreground">
          {reasoningMode === "none" ? t.reasoning_none_hint :
           reasoningMode === "cot" ? t.reasoning_cot_hint : t.reasoning_react_hint}
        </span>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t.docs_col_title}</TableHead>
                <TableHead>{t.docs_col_type}</TableHead>
                <TableHead>{t.docs_col_project}</TableHead>
                <TableHead>{t.docs_col_created}</TableHead>
                <TableHead className="text-right">{t.docs_col_actions}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">{t.common_loading}</TableCell>
                </TableRow>
              ) : documents?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">{t.docs_empty}</TableCell>
                </TableRow>
              ) : (
                documents?.map(doc => (
                  <TableRow key={doc.id} data-testid={`row-doc-${doc.id}`}>
                    <TableCell className="font-medium">
                      <Link href={`/documents/${doc.id}`} className="hover:underline">{doc.title}</Link>
                    </TableCell>
                    <TableCell>
                      <span className="uppercase text-xs font-semibold bg-secondary px-2 py-1 rounded">{doc.doc_type}</span>
                    </TableCell>
                    <TableCell>{doc.project_name || "—"}</TableCell>
                    <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRunReview(doc.id)}
                        disabled={runningReviews.has(doc.id)}
                        data-testid={`button-review-doc-${doc.id}`}
                      >
                        {runningReviews.has(doc.id) ? (
                          <Loader2 className="h-3 w-3 animate-spin mr-1" />
                        ) : null}
                        {runningReviews.has(doc.id) ? t.docs_review_running : t.docs_run_review}
                      </Button>
                      <Button variant="outline" size="sm" asChild data-testid={`button-view-doc-${doc.id}`}>
                        <Link href={`/documents/${doc.id}`}>{t.docs_view}</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          <div className="p-4 border-t flex items-center justify-between">
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}
              data-testid="button-prev-page">{t.common_prev}</Button>
            <span className="text-sm text-muted-foreground">{t.common_page} {page}</span>
            <Button variant="outline" size="sm" disabled={!documents || documents.length < limit}
              onClick={() => setPage(p => p + 1)} data-testid="button-next-page">{t.common_next}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
