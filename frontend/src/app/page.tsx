import { AuthCard } from '@/components/auth-card';

export default function SignupPage() {
  return (
    <section className="px-6 py-12 lg:px-10 lg:py-16">
      <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-docket border border-soot/12 bg-soot p-8 text-paper shadow-docket">
          <p className="font-mono text-xs uppercase tracking-[0.3em] text-paper/55">DeepGuard access</p>
          <h1 className="mt-4 max-w-3xl font-[family-name:var(--font-display)] text-5xl leading-none">
            Create your account first, then investigate image, news, and audio cases from one desk.
          </h1>
          <div className="mt-8 space-y-4 text-sm leading-7 text-paper/75">
            <p>This student project uses account-scoped history, secure cookies, and backend persistence so each user gets their own case log.</p>
            <p>After signup, you will be redirected into the app and can open the teacher demo board or start an investigation immediately.</p>
          </div>
        </div>

        <AuthCard
          title="Create Your DeepGuard Account"
          copy="Sign up to unlock the teacher demo board, case history, and verification flows."
          defaultMode="register"
        />
      </div>
    </section>
  );
}
