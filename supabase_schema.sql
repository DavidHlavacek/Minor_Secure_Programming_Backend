-- Create schema for Gamer CV application

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table (extends Supabase auth.users)
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    bio TEXT,
    avatar_url TEXT,
    timezone TEXT,
    preferred_language TEXT DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create user settings table
CREATE TABLE public.user_settings (
    user_id UUID REFERENCES public.profiles(id) PRIMARY KEY,
    profile_public BOOLEAN DEFAULT FALSE,
    stats_public BOOLEAN DEFAULT FALSE,
    allow_friend_requests BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    stats_update_notifications BOOLEAN DEFAULT TRUE,
    weekly_summary BOOLEAN DEFAULT TRUE,
    theme TEXT DEFAULT 'system',
    default_category TEXT,
    auto_refresh_stats BOOLEAN DEFAULT TRUE,
    stats_refresh_interval INTEGER DEFAULT 3600
);

-- Create game categories table
CREATE TABLE public.game_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    supported_stats BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create games table
CREATE TABLE public.games (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) NOT NULL,
    category_id UUID REFERENCES public.game_categories(id) NOT NULL,
    name TEXT NOT NULL,
    username TEXT NOT NULL,  -- In-game username
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name, username)  -- User can't add same game+username twice
);

-- Create game stats table (JSON for flexible schema)
CREATE TABLE public.game_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id UUID REFERENCES public.games(id) NOT NULL,
    stats_data JSONB NOT NULL,  -- Flexible schema for different game types
    last_refreshed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create activity log
CREATE TABLE public.activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) NOT NULL,
    type TEXT NOT NULL,  -- e.g., 'game_added', 'rank_up', etc.
    title TEXT NOT NULL,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create friend requests table
CREATE TABLE public.friend_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_user_id UUID REFERENCES public.profiles(id) NOT NULL,
    to_user_id UUID REFERENCES public.profiles(id) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'accepted', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(from_user_id, to_user_id)
);

-- Create friends table
CREATE TABLE public.friends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) NOT NULL,
    friend_id UUID REFERENCES public.profiles(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, friend_id),
    CHECK (user_id != friend_id)  -- Can't friend yourself
);

-- Insert default game categories
INSERT INTO public.game_categories (name, description, supported_stats) VALUES
('MOBA', 'Multiplayer Online Battle Arena games like League of Legends, Dota 2', TRUE),
('FPS', 'First Person Shooter games like Valorant, CS:GO', TRUE),
('RPG', 'Role Playing Games like World of Warcraft', TRUE),
('Battle Royale', 'Battle Royale games like Fortnite, PUBG', FALSE),
('Sports', 'Sports games like FIFA, NBA 2K', FALSE);

-- Create Row Level Security Policies

-- Profiles table policies
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow users to read their own profile"
    ON public.profiles
    FOR SELECT
    TO authenticated
    USING (id = auth.uid());

CREATE POLICY "Allow users to update their own profile"
    ON public.profiles
    FOR UPDATE
    TO authenticated
    USING (id = auth.uid());

-- User settings table policies
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow users to read their own settings"
    ON public.user_settings
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Allow users to update their own settings"
    ON public.user_settings
    FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid());

-- Games table policies
ALTER TABLE public.games ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow users to read their own games"
    ON public.games
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Allow users to insert their own games"
    ON public.games
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "Allow users to update their own games"
    ON public.games
    FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Allow users to delete their own games"
    ON public.games
    FOR DELETE
    TO authenticated
    USING (user_id = auth.uid());

-- Game stats policies
ALTER TABLE public.game_stats ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow users to read stats for their games"
    ON public.game_stats
    FOR SELECT
    TO authenticated
    USING (game_id IN (SELECT id FROM public.games WHERE user_id = auth.uid()));

-- Create functions for stats refresh
CREATE OR REPLACE FUNCTION public.refresh_game_stats(game_id UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    game_record RECORD;
    result JSONB;
BEGIN
    -- In a real implementation, this would call external APIs
    -- For now, we'll just return a placeholder
    SELECT g.* INTO game_record FROM public.games g WHERE g.id = game_id;
    
    -- This is where your backend API would fetch and transform the stats
    result = '{"message": "Stats refresh scheduled", "game_id": "' || game_id::text || '"}';
    
    RETURN result;
END;
$$;

-- Create function to handle user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Create profile record
    INSERT INTO public.profiles (id, username, email)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'username', NEW.email);
    
    -- Create default user settings
    INSERT INTO public.user_settings (user_id)
    VALUES (NEW.id);
    
    RETURN NEW;
END;
$$;

-- Trigger for new user creation
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE PROCEDURE public.handle_new_user();
