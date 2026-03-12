import { useMutation } from "@tanstack/react-query";
import { mergePdfs } from "../api/documents";

export function usePdfMerge() {
  return useMutation({
    mutationFn: ({
      recordId,
      fileIds,
    }: {
      recordId: string;
      fileIds: string[];
    }) => mergePdfs(recordId, fileIds),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "merged.pdf";
      a.click();
      URL.revokeObjectURL(url);
    },
  });
}
