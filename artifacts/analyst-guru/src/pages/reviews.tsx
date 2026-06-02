import { useState } from "react";
import { useListReviews, getListReviewsQueryKey } from "@workspace/api-client-react";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";

export default function Reviews() {
  const [page, setPage] = useState(1);
  const limit = 20;
  const offset = (page - 1) * limit;

  const { data: reviews, isLoading } = useListReviews({ limit, offset }, {
    query: {
      queryKey: getListReviewsQueryKey({ limit, offset }),
    }
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Reviews</h1>
          <p className="text-muted-foreground">Analysis results and document checks.</p>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Document</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead>Created At</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">Loading...</TableCell>
                </TableRow>
              ) : reviews?.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">No reviews found.</TableCell>
                </TableRow>
              ) : (
                reviews?.map(review => (
                  <TableRow key={review.id}>
                    <TableCell className="font-medium">
                      <Link href={`/reviews/${review.id}`} className="hover:underline">
                        {review.document_title || review.document_id}
                      </Link>
                    </TableCell>
                    <TableCell>
                      {review.needs_review ? (
                        <span className="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20">
                          ⚠️ Требует проверки
                        </span>
                      ) : (
                        <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                          OK
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
                    <TableCell className="text-right space-x-2">
                      <Button variant="outline" size="sm" asChild>
                        <Link href={`/reviews/${review.id}`}>View Details</Link>
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
            <Button variant="outline" size="sm" disabled={!reviews || reviews.length < limit} onClick={() => setPage(p => p + 1)}>Next</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
