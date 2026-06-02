import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  useListKbDocuments, getListKbDocumentsQueryKey,
  useListKbHistory, getListKbHistoryQueryKey,
  useAskKnowledgeBase
} from "@workspace/api-client-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Search } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

export default function KnowledgeBase() {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState("ask");
  const [question, setQuestion] = useState("");
  const askMutation = useAskKnowledgeBase();
  const [answer, setAnswer] = useState<any>(null);

  const { data: kbDocs, isLoading: kbLoading } = useListKbDocuments({}, {
    query: { queryKey: getListKbDocumentsQueryKey() }
  });

  const { data: history, isLoading: historyLoading } = useListKbHistory({}, {
    query: { queryKey: getListKbHistoryQueryKey() }
  });

  const handleAsk = async () => {
    if (!question.trim()) return;
    try {
      const res = await askMutation.mutateAsync({ data: { question } });
      setAnswer(res);
    } catch (e) {
      console.error(e);
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
                            <p className="font-medium mb-1 text-primary">{src.document_title || t.kb_unknown_doc}</p>
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
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t.kb_docs_col_title}</TableHead>
                    <TableHead>{t.kb_docs_col_project}</TableHead>
                    <TableHead>{t.kb_docs_col_added}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {kbLoading ? (
                    <TableRow><TableCell colSpan={3} className="text-center py-4">{t.common_loading}</TableCell></TableRow>
                  ) : kbDocs?.length === 0 ? (
                    <TableRow><TableCell colSpan={3} className="text-center py-4 text-muted-foreground">{t.kb_docs_empty}</TableCell></TableRow>
                  ) : (
                    kbDocs?.map(doc => (
                      <TableRow key={doc.id}>
                        <TableCell className="font-medium">{doc.title}</TableCell>
                        <TableCell>{doc.project_name || "—"}</TableCell>
                        <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
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
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t.kb_history_col_question}</TableHead>
                    <TableHead>{t.kb_history_col_status}</TableHead>
                    <TableHead>{t.kb_history_col_asked}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {historyLoading ? (
                    <TableRow><TableCell colSpan={3} className="text-center py-4">{t.common_loading}</TableCell></TableRow>
                  ) : history?.length === 0 ? (
                    <TableRow><TableCell colSpan={3} className="text-center py-4 text-muted-foreground">{t.kb_history_empty}</TableCell></TableRow>
                  ) : (
                    history?.map(item => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium truncate max-w-[300px]" title={item.question}>{item.question}</TableCell>
                        <TableCell>
                          {item.needs_review && (
                            <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                              {t.needs_review_badge}
                            </span>
                          )}
                        </TableCell>
                        <TableCell>{new Date(item.created_at).toLocaleDateString()}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
