import { useState } from "react";
import { useListReviews, getListReviewsQueryKey } from "@workspace/api-client-react";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/lib/i18n";

export default function Reviews() {
  const { t } = useLanguage();
  const [page, setPage] = useState(1);
  const limit = 20;
  const offset = (page - 1) * limit;

  const { data: reviews, isLoading } = useListReviews({ limit, offset }, {
    query: { queryKey: getListReviewsQueryKey({ limit, offset }) }
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t.reviews_title}</h1>
          <p className="text-muted-foreground">{t.reviews_subtitle}</p>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t.reviews_col_doc}</TableHead>
                <TableHead>{t.reviews_col_status}</TableHead>
                <TableHead>{t.reviews_col_confidence}</TableHead>
                <TableHead>{t.reviews_col_created}</TableHead>
                <TableHead className="text-right">{t.reviews_col_actions}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">{t.common_loading}</TableCell>
                </TableRow>
              ) : reviews?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">{t.reviews_empty}</TableCell>
                </TableRow>
              ) : (
                reviews?.map(review => (
                  <TableRow key={review.id} data-testid={`row-review-${review.id}`}>
                    <TableCell className="font-medium">
                      <Link href={`/reviews/${review.id}`} className="hover:underline">
                        {review.document_title || review.document_id}
                      </Link>
                    </TableCell>
                    <TableCell>
                      {review.needs_review ? (
                        <span className="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20">
                          {t.needs_review_badge}
                        </span>
                      ) : (
                        <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                          {t.reviews_ok}
                        </span>
                      )}
                    </TableCell>
                    <TableCell>
                      <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                        review.confidence === 'high' ? 'bg-green-50 text-green-700 ring-green-600/20' :
                        review.confidence === 'medium' ? 'bg-yellow-50 text-yellow-800 ring-yellow-600/20' :
                        'bg-red-50 text-red-700 ring-red-600/10'
                      }`}>
                        {review.confidence.toUpperCase()}
                      </span>
                    </TableCell>
                    <TableCell>{new Date(review.created_at).toLocaleString()}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="outline" size="sm" asChild data-testid={`button-view-review-${review.id}`}>
                        <Link href={`/reviews/${review.id}`}>{t.reviews_view}</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          <div className="p-4 border-t flex items-center justify-between">
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>{t.common_prev}</Button>
            <span className="text-sm text-muted-foreground">{t.common_page} {page}</span>
            <Button variant="outline" size="sm" disabled={!reviews || reviews.length < limit} onClick={() => setPage(p => p + 1)}>{t.common_next}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
