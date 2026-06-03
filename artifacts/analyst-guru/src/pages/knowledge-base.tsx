import { useState, useCallback } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  useListKbDocuments, getListKbDocumentsQueryKey,
  useListKbHistory, getListKbHistoryQueryKey,
  useAskKnowledgeBase, useAddKbDocument
} from "@workspace/api-client-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Loader2, Search, ExternalLink, FileText, Plus } from "lucide-react";
import { Link } from "wouter";
import { useLanguage } from "@/lib/i18n";
import { useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";

export default function KnowledgeBase() {
  const { t } = useLanguage();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("ask");
  const [question, setQuestion] = useState("");
  const askMutation = useAskKnowledgeBase();
  const addKbMutation = useAddKbDocument();
  const [answer, setAnswer] = useState<any>(null);
  const [addOpen, setAddOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newText, setNewText] = useState("");
  const [newProject, setNewProject] = useState("");
  const [historyFilter, setHistoryFilter] = useState<string>("all");
  const [detailItem, setDetailItem] = useState<any>(null);

  const { data: kbDocs, isLoading: kbLoading } = useListKbDocuments({}, {
    query: { queryKey: getListKbDocumentsQueryKey() }
  });

  const historyQueryParams = historyFilter === "needs_review" ? { needs_review: true as boolean, limit: 50 as number } : { limit: 50 as number };
  const { data: history, isLoading: historyLoading } = useListKbHistory(historyQueryParams, {
    query: { queryKey: getListKbHistoryQueryKey(historyQueryParams) }
  });

  const handleAsk = useCallback(async () => {
    if (!question.trim()) return;
    try {
      const res = await askMutation.mutateAsync({ data: { question } });
      setAnswer(res);
    } catch (e) {
      console.error(e);
    }
  }, [question, askMutation]);

  const handleAddDocument = async () => {
    if (!newTitle.trim() || !newText.trim()) return;
    try {
      await addKbMutation.mutateAsync({
        data: { title: newTitle, text: newText, project_name: newProject || null, doc_type: "kb_article" }
      });
      toast({ title: t.kb_docs_add_success });
      queryClient.invalidateQueries({ queryKey: getListKbDocumentsQueryKey() });
      setAddOpen(false);
      setNewTitle("");
      setNewText("");
      setNewProject("");
    } catch {
      toast({ title: t.kb_docs_add_error, variant: "destructive" });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">{t.kb_title}</h1>
        <p className="text-muted-foreground">{t.kb_subtitle}</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="ask" data-testid="tab-ask">{t.kb_tab_ask}</TabsTrigger>
          <TabsTrigger value="documents" data-testid="tab-kb-docs">{t.kb_tab_docs}</TabsTrigger>
          <TabsTrigger value="history" data-testid="tab-kb-history">{t.kb_tab_history}</TabsTrigger>
        </TabsList>

        <TabsContent value="ask" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t.kb_ask_title}</CardTitle>
              <CardDescription>{t.kb_ask_desc}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  data-testid="input-kb-question"
                  placeholder={t.kb_ask_placeholder}
                  value={question}
                  onChange={e => setQuestion(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleAsk()}
                />
                <Button
                  onClick={handleAsk}
                  disabled={askMutation.isPending || !question.trim()}
                  data-testid="button-ask-kb"
                >
                  {askMutation.isPending
                    ? <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    : <Search className="h-4 w-4 mr-2" />}
                  {t.kb_ask_btn}
                </Button>
              </div>

              {answer && (
                <div className="mt-8 space-y-6">
                  <div className="bg-muted/50 p-6 rounded-lg border">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-lg">{t.kb_answer_title}</h3>
                      {answer.needs_review && (
                        <span className="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20">
                          {t.needs_review_badge}
                        </span>
                      )}
                    </div>
                    <div className="text-sm leading-relaxed whitespace-pre-wrap">{answer.answer}</div>
                  </div>

                  {answer.sources && answer.sources.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3 text-sm text-muted-foreground uppercase tracking-wider">{t.kb_sources}</h4>
                      <div className="space-y-3">
                        {answer.sources.map((src: any, i: number) => (
                          <div key={i} className="text-sm bg-card border rounded p-3">
                            {src.document_id ? (
                              <Link href={`/documents/${src.document_id}`} className="font-medium mb-1 text-primary hover:underline inline-flex items-center gap-1">
                                {src.document_title || t.kb_unknown_doc}
                                <ExternalLink className="h-3 w-3" />
                              </Link>
                            ) : (
                              <p className="font-medium mb-1 text-primary">{src.document_title || t.kb_unknown_doc}</p>
                            )}
                            <p className="text-muted-foreground italic border-l-2 pl-3 mt-2">{src.quote}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="documents">
          <Card>
            <div className="p-4 border-b flex items-center justify-between">
              <p className="text-sm text-muted-foreground">{kbDocs?.length || 0} {t.kb_docs_col_title?.toLowerCase?.() || "документов"}</p>
              <Button onClick={() => setAddOpen(true)} size="sm" data-testid="button-add-kb-doc">
                <Plus className="h-4 w-4 mr-1" />
                {t.kb_docs_add}
              </Button>
            </div>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t.kb_docs_col_title}</TableHead>
                    <TableHead className="hidden md:table-cell">{t.kb_docs_col_id}</TableHead>
                    <TableHead className="hidden md:table-cell">{t.kb_docs_col_project}</TableHead>
                    <TableHead>{t.kb_docs_col_added}</TableHead>
                    <TableHead className="text-right">{t.kb_docs_col_actions}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {kbLoading ? (
                    <TableRow><TableCell colSpan={5} className="text-center py-8">{t.common_loading}</TableCell></TableRow>
                  ) : kbDocs?.length === 0 ? (
                    <TableRow><TableCell colSpan={5} className="text-center py-8 text-muted-foreground">{t.kb_docs_empty}</TableCell></TableRow>
                  ) : (
                    kbDocs?.map(doc => (
                      <TableRow key={doc.id}>
                        <TableCell className="font-medium">{doc.title}</TableCell>
                        <TableCell className="hidden md:table-cell text-xs text-muted-foreground font-mono">{doc.id?.slice(0, 8)}…</TableCell>
                        <TableCell className="hidden md:table-cell">{doc.project_name || "—"}</TableCell>
                        <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                        <TableCell className="text-right">
                          <Button variant="outline" size="sm" asChild data-testid={`button-open-kb-doc-${doc.id}`}>
                            <Link href={`/documents/${doc.id}`}>
                              {t.kb_docs_open}
                            </Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history">
          <Card>
            <div className="p-4 border-b flex items-center gap-2">
              <p className="text-sm text-muted-foreground mr-2">{t.kb_history_col_status}:</p>
              <Select value={historyFilter} onValueChange={setHistoryFilter}>
                <SelectTrigger className="w-48" data-testid="select-history-filter">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t.kb_history_filter_all}</SelectItem>
                  <SelectItem value="needs_review">{t.kb_history_filter_needs_review}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t.kb_history_col_question}</TableHead>
                    <TableHead>{t.kb_history_col_status}</TableHead>
                    <TableHead>{t.kb_history_col_asked}</TableHead>
                    <TableHead className="text-right">{t.kb_history_col_actions}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {historyLoading ? (
                    <TableRow><TableCell colSpan={4} className="text-center py-8">{t.common_loading}</TableCell></TableRow>
                  ) : history?.length === 0 ? (
                    <TableRow><TableCell colSpan={4} className="text-center py-8 text-muted-foreground">{t.kb_history_empty}</TableCell></TableRow>
                  ) : (
                    history?.map(item => (
                      <TableRow key={item.id} className="cursor-pointer hover:bg-muted/50" onClick={() => setDetailItem(item)}>
                        <TableCell className="font-medium truncate max-w-[300px]" title={item.question}>{item.question}</TableCell>
                        <TableCell>
                          {item.needs_review ? (
                            <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded whitespace-nowrap">
                              {t.needs_review_badge}
                            </span>
                          ) : (
                            <span className="text-xs text-green-600">OK</span>
                          )}
                        </TableCell>
                        <TableCell className="whitespace-nowrap">{new Date(item.created_at).toLocaleDateString()}</TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setDetailItem(item); }}>
                            <FileText className="h-4 w-4 mr-1" />
                            {t.kb_history_open}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>{t.kb_docs_add_title}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>{t.docs_title_field}</Label>
              <Input value={newTitle} onChange={e => setNewTitle(e.target.value)} placeholder={t.docs_title_placeholder} />
            </div>
            <div className="space-y-2">
              <Label>{t.docs_project_field}</Label>
              <Input value={newProject} onChange={e => setNewProject(e.target.value)} placeholder={t.docs_project_placeholder} />
            </div>
            <div className="space-y-2">
              <Label>{t.docs_content_field}</Label>
              <Textarea value={newText} onChange={e => setNewText(e.target.value)} placeholder={t.docs_content_placeholder} className="h-40 font-mono text-sm" />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setAddOpen(false)}>{t.docs_cancel}</Button>
            <Button onClick={handleAddDocument} disabled={addKbMutation.isPending}>
              {addKbMutation.isPending ? t.docs_saving : t.docs_save}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={!!detailItem} onOpenChange={(open) => { if (!open) setDetailItem(null); }}>
        <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t.kb_history_detail_title}</DialogTitle>
            {detailItem && (
              <DialogDescription className="text-sm font-medium text-foreground/80 pt-2">
                {detailItem.question}
              </DialogDescription>
            )}
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-sm text-muted-foreground mb-2">{t.kb_history_detail_answer}</h4>
              <div className="bg-muted/50 p-4 rounded-md text-sm leading-relaxed whitespace-pre-wrap">{detailItem?.answer || "—"}</div>
            </div>
            {detailItem?.error && (
              <div>
                <h4 className="font-semibold text-sm text-muted-foreground mb-2">{t.kb_history_detail_error}</h4>
                <div className="bg-red-50 text-red-800 p-3 rounded-md text-sm font-mono">{detailItem.error}</div>
              </div>
            )}
            {detailItem?.sources_json && detailItem.sources_json.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm text-muted-foreground mb-2">{t.kb_history_detail_sources}</h4>
                <div className="space-y-2">
                  {detailItem.sources_json.map((src: any, i: number) => (
                    <div key={i} className="text-sm bg-card border rounded p-3">
                      {src.document_id ? (
                        <Link href={`/documents/${src.document_id}`} className="font-medium text-primary hover:underline inline-flex items-center gap-1">
                          {src.document_title || t.kb_unknown_doc}
                          <ExternalLink className="h-3 w-3" />
                        </Link>
                      ) : (
                        <p className="font-medium text-primary">{src.document_title || t.kb_unknown_doc}</p>
                      )}
                      <p className="text-muted-foreground italic border-l-2 pl-3 mt-1 text-xs">{src.quote}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
