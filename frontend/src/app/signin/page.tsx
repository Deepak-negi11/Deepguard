import { AuthCard } from '@/components/auth-card';

export default function SigninPage() {
  return (
    <section className="px-6 py-12 lg:px-10 lg:py-16">
      <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-docket border border-soot/12 bg-white/78 p-8 shadow-docket">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-soot/50">Return to workspace</p>
          <h1 className="mt-4 max-w-3xl font-[family-name:var(--font-display)] text-5xl leading-none text-soot">
            Sign in to continue with your existing DeepGuard account.
          </h1>
          <div className="mt-8 space-y-4 text-sm leading-7 text-soot/72">
            <p>Your account keeps your own verification history, result polling state, and case records separate from other users.</p>
            <p>If the backend is running, successful sign-in will take you straight into the app.</p>
          </div>
        </div>

        <AuthCard
          title="Sign In To DeepGuard"
          copy="Use the same email and password you used during signup."
          defaultMode="login"
        />
      </div>
    </section>
  );
}
