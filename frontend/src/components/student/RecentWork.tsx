"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { FileImage, ChevronDown, ChevronUp } from "lucide-react";

interface Document {
  id: string;
  status: string;
  doc_type: string;
  upload_date: string;
  message?: string;
}

interface Props {
  studentId: string;
}

export function RecentWork({ studentId }: Props) {
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/students/${studentId}/documents`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setDocs)
      .finally(() => setLoading(false));
  }, [studentId]);

  if (loading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    );
  }

  if (docs.length === 0) {
    return (
      <div className="text-center py-6">
        <FileImage className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
        <p className="text-sm text-muted-foreground">
          No work scanned yet. Use &ldquo;Scan Work&rdquo; to capture student artifacts.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {docs.map((doc) => {
        const isExpanded = expandedId === doc.id;
        return (
          <Card key={doc.id}>
            <CardContent className="p-3">
              <button
                type="button"
                className="w-full text-left flex items-center gap-3"
                onClick={() => setExpandedId(isExpanded ? null : doc.id)}
              >
                <div className="w-10 h-10 rounded bg-muted flex items-center justify-center shrink-0">
                  <FileImage className="h-5 w-5 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium truncate">
                      {doc.doc_type.replace("_", " ")}
                    </span>
                    <Badge
                      variant="outline"
                      className="text-[10px] px-1.5 py-0 h-4"
                    >
                      {doc.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {doc.upload_date}
                  </p>
                </div>
                {isExpanded ? (
                  <ChevronUp className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                )}
              </button>
              {isExpanded && doc.message && (
                <div className="mt-2 pt-2 border-t border-border">
                  <p className="text-xs text-muted-foreground">{doc.message}</p>
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
