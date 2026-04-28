export function formatReply(text: string): string {
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // code blocks
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
  // inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  // bold
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  // italic
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  // images ![alt](url)
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="max-w-full rounded-lg my-2" />')
  // links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener" class="text-blue-500 underline">$1</a>')
  // headings
  html = html.replace(/^### (.+)$/gm, '<h4 class="text-sm font-semibold mt-3 mb-1">$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3 class="text-base font-semibold mt-3 mb-1">$1</h3>')
  html = html.replace(/^# (.+)$/gm, '<h3 class="text-base font-semibold mt-3 mb-1">$1</h3>')
  // unordered lists
  html = html.replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
  // line breaks
  html = html.replace(/\n\n/g, '</p><p class="mb-2">')
  html = html.replace(/\n/g, '<br/>')
  html = '<p class="mb-2">' + html + '</p>'

  return html
}
