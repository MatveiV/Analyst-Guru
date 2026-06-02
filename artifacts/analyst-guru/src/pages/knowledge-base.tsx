import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useListKbDocuments, getListKbDocumentsQueryKey, useListKbHistory, getListKbHistoryQueryKey, useAskKnowledgeBase } from "@workspace/api-client-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Search } from "lucide-react";

export default function KnowledgeBase() {
  const [activeTab, setActiveTab] = useState("ask");
  const [question, setQuestion] = useState("");
  const askMutation = useAskKnowledgeBase();
  const [answer, setAnswer] = useState<any>(null);

  const { data: kbDocs, isLoading: kbLoading } = useListKbDocuments({}, {
    query: {
      queryKey: getListKbDocumentsQueryKey(),
    }
  });

  const { data: history, isLoading: historyLoading } = useListKbHistory({}, {
    query: {
      queryKey: getListKbHistoryQueryKey(),
    }
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
        <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
        <p className="text-muted-foreground">RAG-powered search across indexed artifacts.</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="ask">Ask AI</TabsTrigger>
          <TabsTrigger value="documents">Indexed Documents</TabsTrigger>
          <TabsTrigger value="history">Q&A History</TabsTrigger>
        </TabsList>
        
        <TabsContent value="ask" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Ask a Question</CardTitle>
              <CardDescription>Search across all project documentation and decisions.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input 
                  placeholder="E.g. What is the authentication mechanism for Project Alpha?" 
                  value={question}
                  onChange={e => setQuestion(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleAsk()}
                />
                <Button onClick={handleAsk} disabled={askMutation.isPending || !question.trim()}>
                  {askMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Search className="h-4 w-4 mr-2" />}
                  Ask
                </Button>
              </div>

              {answer && (
                <div className="mt-8 space-y-6">
                  <div className="bg-muted/50 p-6 rounded-lg border">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-lg">Answer</h3>
                      {answer.needs_review && (
                        <span className="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20">
                          ⚠️ Требует проверки
                        </span>
                      )}
                    </div>
                    <div className="text-sm leading-relaxed whitespace-pre-wrap">{answer.answer}</div>
                  </div>
                  
                  {answer.sources && answer.sources.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3 text-sm text-muted-foreground uppercase tracking-wider">Sources</h4>
                      <div className="space-y-3">
                        {answer.sources.map((src: any, i: number) => (
                          <div key={i} className="text-sm bg-card border rounded p-3">
                            <p className="font-medium mb-1 text-primary">{src.document_title || "Unknown Document"}</p>
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
                    <TableHead>Title</TableHead>
                    <TableHead>Project</TableHead>
                    <TableHead>Added</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {kbLoading ? (
                    <TableRow><TableCell colSpan={3} className="text-center py-4">Loading...</TableCell></TableRow>
                  ) : kbDocs?.length === 0 ? (
                    <TableRow><TableCell colSpan={3} className="text-center py-4 text-muted-foreground">No documents in KB.</TableCell></TableRow>
                  ) : (
                    kbDocs?.map(doc => (
                      <TableRow key={doc.id}>
                        <TableCell className="font-medium">{doc.title}</TableCell>
                        <TableCell>{doc.project_name || "-"}</TableCell>
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
                    <TableHead>Question</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Asked At</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {historyLoading ? (
                    <TableRow><TableCell colSpan={3} className="text-center py-4">Loading...</TableCell></TableRow>
                  ) : history?.length === 0 ? (
                    <TableRow><TableCell colSpan={3} className="text-center py-4 text-muted-foreground">No history.</TableCell></TableRow>
                  ) : (
                    history?.map(item => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium truncate max-w-[300px]" title={item.question}>{item.question}</TableCell>
                        <TableCell>
                          {item.needs_review && <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">⚠️ Review</span>}
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
