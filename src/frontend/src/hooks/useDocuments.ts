import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listInvestigationDocuments,
  uploadDocument,
  deleteDocument,
} from "../api/documents";

export function useDocuments(investigationId: string, page = 1) {
  return useQuery({
    queryKey: ["documents", investigationId, page],
    queryFn: () => listInvestigationDocuments(investigationId, page),
    enabled: !!investigationId,
    // Poll every 10s while any document has a pending/processing PDF conversion
    refetchInterval: (query) => {
      const hasPending = query.state.data?.data.some(
        (doc) =>
          doc.pdf_conversion_status === "pending" ||
          doc.pdf_conversion_status === "processing",
      );
      return hasPending ? 10_000 : false;
    },
  });
}

export function useUploadDocument(investigationId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => uploadDocument(investigationId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["documents", investigationId],
      });
    },
  });
}

export function useDeleteDocument(investigationId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) => deleteDocument(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["documents", investigationId],
      });
    },
  });
}
