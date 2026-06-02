import { useState } from "react";
import { useListDocuments, getListDocumentsQueryKey, useCreateDocument } from "@workspace/api-client-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Link } from "wouter";
import { useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export default function Documents() {
  const [page, setPage] = useState(1);
  const limit = 20;
  const offset = (page - 1) * limit;

  const { data: documents, isLoading } = useListDocuments({ limit, offset }, {
    query: {
      queryKey: getListDocumentsQueryKey({ limit, offset }),
    }
  });

  const queryClient = useQueryClient();
  const { toast } = useToast();

  const createDocMutation = useCreateDocument();
  const [open, setOpen] = useState(false);

  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [docType, setDocType] = useState("tz");
  const [projectName, setProjectName] = useState("");

  const handleCreate = async () => {
    if (!title || !text) return;
    try {
      await createDocMutation.mutateAsync({
        data: {
          title,
          text,
          doc_type: docType,
          project_name: projectName || null,
        }
      });
      toast({ title: "Document created successfully" });
      queryClient.invalidateQueries({ queryKey: getListDocumentsQueryKey({ limit, offset }) });
      setOpen(false);
      setTitle("");
      setText("");
    } catch (e) {
      toast({ title: "Failed to create document", variant: "destructive" });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground">Manage and review project documentation.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>Add Document</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>Add New Document</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Title</Label>
                <Input value={title} onChange={e => setTitle(e.target.value)} placeholder="E.g. Payment Gateway Requirements" />
              </div>
              <div className="space-y-2">
                <Label>Type</Label>
                <Select value={docType} onValueChange={setDocType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
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
                <Label>Project Name (Optional)</Label>
                <Input value={projectName} onChange={e => setProjectName(e.target.value)} placeholder="Project Alpha" />
              </div>
              <div className="space-y-2">
                <Label>Content</Label>
                <Textarea value={text} onChange={e => setText(e.target.value)} placeholder="Paste document content here..." className="h-40 font-mono text-sm" />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={createDocMutation.isPending}>
                {createDocMutation.isPending ? "Saving..." : "Save Document"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Project</TableHead>
                <TableHead>Created At</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">Loading...</TableCell>
                </TableRow>
              ) : documents?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">No documents found.</TableCell>
                </TableRow>
              ) : (
                documents?.map(doc => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium">
                      <Link href={`/documents/${doc.id}`} className="hover:underline">{doc.title}</Link>
                    </TableCell>
                    <TableCell><span className="uppercase text-xs font-semibold bg-secondary px-2 py-1 rounded">{doc.doc_type}</span></TableCell>
                    <TableCell>{doc.project_name || "-"}</TableCell>
                    <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button variant="outline" size="sm" asChild>
                        <Link href={`/documents/${doc.id}`}>View</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
          
          <div className="p-4 border-t flex items-center justify-between">
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Previous</Button>
            <span className="text-sm text-muted-foreground">Page {page}</span>
            <Button variant="outline" size="sm" disabled={!documents || documents.length < limit} onClick={() => setPage(p => p + 1)}>Next</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
