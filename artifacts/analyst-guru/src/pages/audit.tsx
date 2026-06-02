import { useState } from "react";
import { useListAuditRuns, getListAuditRunsQueryKey } from "@workspace/api-client-react";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

export default function Audit() {
  const { t } = useLanguage();
  const [page, setPage] = useState(1);
  const limit = 20;
  const offset = (page - 1) * limit;

  const { data: runs, isLoading } = useListAuditRuns({ limit, offset }, {
    query: { queryKey: getListAuditRunsQueryKey({ limit, offset }) }
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t.audit_title}</h1>
        <p className="text-muted-foreground">{t.audit_subtitle}</p>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t.audit_col_action}</TableHead>
                <TableHead>{t.audit_col_status}</TableHead>
                <TableHead>{t.audit_col_duration}</TableHead>
                <TableHead>{t.audit_col_executed}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin mx-auto text-muted-foreground" />
                  </TableCell>
                </TableRow>
              ) : runs?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">{t.audit_empty}</TableCell>
                </TableRow>
              ) : (
                runs?.map(run => (
                  <TableRow key={run.id} data-testid={`row-audit-${run.id}`}>
                    <TableCell className="font-mono text-sm">{run.action}</TableCell>
                    <TableCell>
                      <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                        run.status === 'ok' ? 'bg-green-50 text-green-700 ring-green-600/20' :
                        run.status === 'error' ? 'bg-red-50 text-red-700 ring-red-600/10' :
                        'bg-yellow-50 text-yellow-800 ring-yellow-600/20'
                      }`}>
                        {run.status.toUpperCase()}
                      </span>
                    </TableCell>
                    <TableCell>{run.duration_ms}ms</TableCell>
                    <TableCell>{new Date(run.created_at).toLocaleString()}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          <div className="p-4 border-t flex items-center justify-between">
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>{t.common_prev}</Button>
            <span className="text-sm text-muted-foreground">{t.common_page} {page}</span>
            <Button variant="outline" size="sm" disabled={!runs || runs.length < limit} onClick={() => setPage(p => p + 1)}>{t.common_next}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
