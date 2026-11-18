declare module '@deepseek-ai/dsh-llm/message' {
    interface MessageSourceMap {
        /** A notice dsh-github-bot queued for the model on a human command's behalf. */
        'dsh-github-bot': {
            kind: 'dsh-github-bot';
        } & ContextFormed;
    }
}
export {};
//# sourceMappingURL=message-source.d.ts.map