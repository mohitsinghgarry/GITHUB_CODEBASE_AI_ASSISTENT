export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-4">GitHub Codebase RAG Assistant</h1>
        <p className="text-lg text-muted-foreground">
          AI-powered code exploration and analysis tool
        </p>
        <div className="mt-8">
          <p className="text-sm text-muted-foreground">
            Frontend is ready. Start building your components!
          </p>
        </div>
      </div>
    </main>
  );
}
