
-- CTF Events
CREATE TABLE ctf_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL DEFAULT '',
  start_date TIMESTAMPTZ NOT NULL,
  end_date TIMESTAMPTZ NOT NULL,
  is_public BOOLEAN NOT NULL DEFAULT true,
  status TEXT NOT NULL DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'running', 'finished', 'cancelled')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID REFERENCES auth.users(id)
);

-- Challenge Categories
CREATE TABLE challenge_categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  icon TEXT NOT NULL DEFAULT 'shield',
  color TEXT NOT NULL DEFAULT 'blue',
  sort_order INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Challenges
CREATE TABLE challenges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID NOT NULL REFERENCES ctf_events(id) ON DELETE CASCADE,
  category_id UUID NOT NULL REFERENCES challenge_categories(id),
  title TEXT NOT NULL,
  slug TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  point_value INT NOT NULL DEFAULT 100,
  difficulty TEXT NOT NULL DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard', 'insane')),
  flag TEXT NOT NULL,
  hint TEXT DEFAULT '',
  is_active BOOLEAN NOT NULL DEFAULT true,
  solve_count INT NOT NULL DEFAULT 0,
  author TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(event_id, slug)
);

-- Teams
CREATE TABLE teams (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID NOT NULL REFERENCES ctf_events(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID REFERENCES auth.users(id),
  UNIQUE(event_id, slug)
);

-- Team Members (join table)
CREATE TABLE team_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('captain', 'member')),
  joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(team_id, user_id)
);

-- Submissions (flag attempts)
CREATE TABLE submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  challenge_id UUID NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id),
  team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
  event_id UUID NOT NULL REFERENCES ctf_events(id) ON DELETE CASCADE,
  submitted_flag TEXT NOT NULL,
  is_correct BOOLEAN NOT NULL DEFAULT false,
  ip_address TEXT DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Solve announcements
CREATE TABLE solves (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  challenge_id UUID NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id),
  team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
  event_id UUID NOT NULL REFERENCES ctf_events(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(challenge_id, user_id)
);

-- Enable RLS on all tables
ALTER TABLE ctf_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE challenge_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE solves ENABLE ROW LEVEL SECURITY;

-- RLS policies for ctf_events
CREATE POLICY "select_ctf_events" ON ctf_events FOR SELECT TO authenticated USING (true);
CREATE POLICY "insert_ctf_events" ON ctf_events FOR INSERT TO authenticated WITH CHECK (auth.uid() = created_by);
CREATE POLICY "update_ctf_events" ON ctf_events FOR UPDATE TO authenticated USING (auth.uid() = created_by);
CREATE POLICY "delete_ctf_events" ON ctf_events FOR DELETE TO authenticated USING (auth.uid() = created_by);

-- RLS policies for challenge_categories (read-only for all, manage by auth)
CREATE POLICY "select_categories" ON challenge_categories FOR SELECT TO authenticated USING (true);
CREATE POLICY "insert_categories" ON challenge_categories FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "update_categories" ON challenge_categories FOR UPDATE TO authenticated USING (true);
CREATE POLICY "delete_categories" ON challenge_categories FOR DELETE TO authenticated USING (true);

-- RLS policies for challenges
CREATE POLICY "select_challenges" ON challenges FOR SELECT TO authenticated USING (true);
CREATE POLICY "insert_challenges" ON challenges FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "update_challenges" ON challenges FOR UPDATE TO authenticated USING (true);
CREATE POLICY "delete_challenges" ON challenges FOR DELETE TO authenticated USING (true);

-- RLS policies for teams
CREATE POLICY "select_teams" ON teams FOR SELECT TO authenticated USING (true);
CREATE POLICY "insert_teams" ON teams FOR INSERT TO authenticated WITH CHECK (auth.uid() = created_by);
CREATE POLICY "update_teams" ON teams FOR UPDATE TO authenticated USING (auth.uid() = created_by);
CREATE POLICY "delete_teams" ON teams FOR DELETE TO authenticated USING (auth.uid() = created_by);

-- RLS policies for team_members
CREATE POLICY "select_team_members" ON team_members FOR SELECT TO authenticated USING (true);
CREATE POLICY "insert_team_members" ON team_members FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "update_team_members" ON team_members FOR UPDATE TO authenticated USING (true);
CREATE POLICY "delete_team_members" ON team_members FOR DELETE TO authenticated USING (true);

-- RLS policies for submissions
CREATE POLICY "select_submissions" ON submissions FOR SELECT TO authenticated USING (true);
CREATE POLICY "insert_submissions" ON submissions FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "update_submissions" ON submissions FOR UPDATE TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "delete_submissions" ON submissions FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- RLS policies for solves
CREATE POLICY "select_solves" ON solves FOR SELECT TO authenticated USING (true);
CREATE POLICY "insert_solves" ON solves FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "update_solves" ON solves FOR UPDATE TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "delete_solves" ON solves FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_challenges_event ON challenges(event_id);
CREATE INDEX idx_challenges_category ON challenges(category_id);
CREATE INDEX idx_submissions_challenge ON submissions(challenge_id);
CREATE INDEX idx_submissions_user ON submissions(user_id);
CREATE INDEX idx_solves_challenge ON solves(challenge_id);
CREATE INDEX idx_solves_team ON solves(team_id);
CREATE INDEX idx_teams_event ON teams(event_id);
CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_user ON team_members(user_id);
