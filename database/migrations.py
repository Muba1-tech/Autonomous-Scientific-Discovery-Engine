import sqlite3

def ensure_column_exists(cursor: sqlite3.Cursor, table_name: str, column_name: str, column_type: str):
    """Safely adds missing columns to existing SQLite tables without breaking legacy data."""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        if column_name not in columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
    except Exception as e:
        print(f"[Migration Warning] Could not alter table {table_name} for column {column_name}: {e}")

def run_migrations(conn: sqlite3.Connection):
    """
    Creates or upgrades SQLite database tables for PROJECT AION.
    Preserves existing data in 'papers' and 'hypotheses' while auto-healing missing columns.
    """
    cursor = conn.cursor()

    # 1. papers table
    cursor.execute('''CREATE TABLE IF NOT EXISTS papers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_id TEXT,
        title TEXT NOT NULL,
        abstract TEXT,
        source TEXT,
        url TEXT,
        authors TEXT,
        year INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    ensure_column_exists(cursor, "papers", "research_id", "TEXT")
    ensure_column_exists(cursor, "papers", "url", "TEXT")
    ensure_column_exists(cursor, "papers", "authors", "TEXT")
    ensure_column_exists(cursor, "papers", "year", "INTEGER")

    # 2. research_gaps table
    cursor.execute('''CREATE TABLE IF NOT EXISTS research_gaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gap_id TEXT UNIQUE,
        research_id TEXT,
        topic TEXT,
        description TEXT,
        supporting_papers TEXT,
        evidence TEXT,
        paper_count INTEGER,
        confidence_score REAL,
        potential_direction TEXT,
        related_concepts TEXT,
        research_domain TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 3. concepts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS concepts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        domain TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 4. hypotheses table
    cursor.execute('''CREATE TABLE IF NOT EXISTS hypotheses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_id TEXT,
        content TEXT NOT NULL,
        verdict TEXT,
        score REAL,
        domain TEXT,
        title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    ensure_column_exists(cursor, "hypotheses", "research_id", "TEXT")
    ensure_column_exists(cursor, "hypotheses", "domain", "TEXT")
    ensure_column_exists(cursor, "hypotheses", "title", "TEXT")

    # 5. hypothesis_scores table
    cursor.execute('''CREATE TABLE IF NOT EXISTS hypothesis_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hypothesis_id INTEGER,
        research_id TEXT,
        novelty_score REAL,
        feasibility_score REAL,
        potential_impact_score REAL,
        evidence_strength REAL,
        priority_score REAL,
        sub_metrics TEXT,
        FOREIGN KEY(hypothesis_id) REFERENCES hypotheses(id)
    )''')

    # 6. experiments table
    cursor.execute('''CREATE TABLE IF NOT EXISTS experiments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_id TEXT,
        hypothesis_id INTEGER,
        experiment_type TEXT,
        variables TEXT,
        methodology TEXT,
        config TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 7. experiment_results table
    cursor.execute('''CREATE TABLE IF NOT EXISTS experiment_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        experiment_id INTEGER,
        research_id TEXT,
        simulated_feasibility REAL,
        outcome_status TEXT,
        metrics_json TEXT,
        sandbox_log TEXT,
        plots_json TEXT,
        limitations TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(experiment_id) REFERENCES experiments(id)
    )''')

    # 8. citations table
    cursor.execute('''CREATE TABLE IF NOT EXISTS citations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_id TEXT,
        claim_text TEXT,
        source_title TEXT,
        url TEXT,
        confidence REAL
    )''')

    # 9. citation_verifications table
    cursor.execute('''CREATE TABLE IF NOT EXISTS citation_verifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_id TEXT,
        claim_text TEXT,
        status TEXT,
        supporting_source TEXT,
        relevant_evidence TEXT,
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 10. research_sessions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS research_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_id TEXT UNIQUE,
        domain_goal TEXT,
        research_goal TEXT,
        timestamp TEXT,
        status TEXT,
        paper_count INTEGER,
        gap_count INTEGER,
        hypothesis_count INTEGER,
        overall_priority_score REAL
    )''')

    # 11. research_history table
    cursor.execute('''CREATE TABLE IF NOT EXISTS research_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_id TEXT UNIQUE,
        domain TEXT,
        question TEXT,
        papers_json TEXT,
        gaps_json TEXT,
        hypothesis_text TEXT,
        scores_json TEXT,
        experiment_json TEXT,
        verifications_json TEXT,
        explainability_json TEXT,
        report_markdown TEXT,
        package_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 12. agent_memory table
    cursor.execute('''CREATE TABLE IF NOT EXISTS agent_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_id TEXT,
        domain TEXT,
        hypothesis TEXT,
        evidence TEXT,
        methodology TEXT,
        experiment_result TEXT,
        outcome TEXT,
        user_feedback TEXT,
        novelty_score REAL,
        feasibility_score REAL,
        impact_score REAL,
        patterns_extracted TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 13. knowledge_relationships table
    cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge_relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_node TEXT,
        source_type TEXT,
        target_node TEXT,
        target_type TEXT,
        relation_type TEXT,
        research_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 14. cross_domain_connections table
    cursor.execute('''CREATE TABLE IF NOT EXISTS cross_domain_connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        research_id TEXT,
        source_domain TEXT,
        target_domain TEXT,
        transferred_concept TEXT,
        rationale TEXT,
        novelty_score REAL,
        impact_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 14b. user_feedback table (1 to 5 star rating & user preferences)
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT,
        hypothesis_title TEXT,
        rating INTEGER,
        feedback_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # ========================================================================
    # PROJECT AION — Advanced Autonomous Scientist Upgrade Tables
    # ========================================================================

    # 15. missions table — Research mission lifecycle
    cursor.execute('''CREATE TABLE IF NOT EXISTS missions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mission_id TEXT UNIQUE NOT NULL,
        objective TEXT NOT NULL,
        domain TEXT,
        mode TEXT DEFAULT 'DEEP_RESEARCH',
        status TEXT DEFAULT 'PENDING',
        user_constraints TEXT DEFAULT '',
        research_depth INTEGER DEFAULT 5,
        agent_budget INTEGER DEFAULT 100,
        literature_budget INTEGER DEFAULT 50,
        hypothesis_budget INTEGER DEFAULT 20,
        simulation_budget INTEGER DEFAULT 50,
        time_limit_hours REAL DEFAULT 2.0,
        progress REAL DEFAULT 0.0,
        current_phase TEXT DEFAULT '',
        papers_found INTEGER DEFAULT 0,
        claims_extracted INTEGER DEFAULT 0,
        hypotheses_generated INTEGER DEFAULT 0,
        hypotheses_survived INTEGER DEFAULT 0,
        experiments_run INTEGER DEFAULT 0,
        falsification_tests INTEGER DEFAULT 0,
        peer_reviews INTEGER DEFAULT 0,
        discovery_index REAL DEFAULT 0.0,
        findings_json TEXT DEFAULT '{}',
        evidence_json TEXT DEFAULT '[]',
        checkpoint_json TEXT DEFAULT '{}',
        error_message TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )''')

    # 16. agent_runs table — Individual agent execution records
    cursor.execute('''CREATE TABLE IF NOT EXISTS agent_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mission_id TEXT,
        research_id TEXT,
        agent_role TEXT NOT NULL,
        agent_class TEXT,
        status TEXT DEFAULT 'PENDING',
        input_summary TEXT DEFAULT '',
        output_summary TEXT DEFAULT '',
        output_data_json TEXT DEFAULT '{}',
        confidence REAL DEFAULT 0.0,
        execution_time_seconds REAL DEFAULT 0.0,
        token_usage_json TEXT DEFAULT '{}',
        error_message TEXT DEFAULT '',
        attempt_number INTEGER DEFAULT 1,
        started_at TIMESTAMP,
        completed_at TIMESTAMP
    )''')

    # 17. mission_events table — Activity log for missions
    cursor.execute('''CREATE TABLE IF NOT EXISTS mission_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mission_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        message TEXT NOT NULL,
        agent_role TEXT DEFAULT '',
        phase TEXT DEFAULT '',
        data_json TEXT DEFAULT '{}',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 18. evolving_hypotheses table — Evolutionary hypothesis population
    cursor.execute('''CREATE TABLE IF NOT EXISTS evolving_hypotheses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hypothesis_id TEXT UNIQUE NOT NULL,
        mission_id TEXT NOT NULL,
        research_id TEXT,
        statement TEXT NOT NULL,
        domain TEXT,
        generation INTEGER DEFAULT 0,
        parent_ids_json TEXT DEFAULT '[]',
        assumptions_json TEXT DEFAULT '[]',
        supporting_evidence_json TEXT DEFAULT '[]',
        contradicting_evidence_json TEXT DEFAULT '[]',
        novelty_score REAL DEFAULT 0.0,
        evidence_score REAL DEFAULT 0.0,
        feasibility_score REAL DEFAULT 0.0,
        impact_score REAL DEFAULT 0.0,
        falsifiability_score REAL DEFAULT 0.0,
        reproducibility_score REAL DEFAULT 0.0,
        confidence REAL DEFAULT 0.0,
        uncertainty REAL DEFAULT 1.0,
        status TEXT DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 19. debates table — Scientific debate arena records
    cursor.execute('''CREATE TABLE IF NOT EXISTS debates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        debate_id TEXT UNIQUE NOT NULL,
        mission_id TEXT,
        hypothesis_id TEXT,
        advocate_arguments_json TEXT DEFAULT '[]',
        skeptic_arguments_json TEXT DEFAULT '[]',
        evidence_used_json TEXT DEFAULT '[]',
        evidence_quality REAL DEFAULT 0.0,
        logical_weaknesses_json TEXT DEFAULT '[]',
        unresolved_questions_json TEXT DEFAULT '[]',
        methodology_review TEXT DEFAULT '',
        statistical_review TEXT DEFAULT '',
        verdict TEXT DEFAULT 'UNCERTAIN',
        judge_rationale TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 20. peer_reviews table — Structured peer review records
    cursor.execute('''CREATE TABLE IF NOT EXISTS peer_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        review_id TEXT UNIQUE NOT NULL,
        mission_id TEXT,
        research_id TEXT,
        reviewer_role TEXT DEFAULT 'PeerReviewer',
        methodology_assessment TEXT DEFAULT '',
        evidence_assessment TEXT DEFAULT '',
        reproducibility_assessment TEXT DEFAULT '',
        statistical_validity TEXT DEFAULT '',
        strengths_json TEXT DEFAULT '[]',
        weaknesses_json TEXT DEFAULT '[]',
        recommendations_json TEXT DEFAULT '[]',
        overall_quality_score REAL DEFAULT 0.0,
        confidence REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 21. falsification_results table — Falsification test outcomes
    cursor.execute('''CREATE TABLE IF NOT EXISTS falsification_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        falsification_id TEXT UNIQUE NOT NULL,
        mission_id TEXT,
        hypothesis_id TEXT,
        criterion TEXT NOT NULL,
        test_description TEXT NOT NULL,
        test_type TEXT DEFAULT 'conceptual',
        evidence_json TEXT DEFAULT '{}',
        result TEXT DEFAULT 'INCONCLUSIVE',
        explanation TEXT DEFAULT '',
        confidence REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 22. contradiction_records table — Contradictory evidence tracking
    cursor.execute('''CREATE TABLE IF NOT EXISTS contradiction_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contradiction_id TEXT UNIQUE NOT NULL,
        mission_id TEXT,
        claim_text TEXT NOT NULL,
        claim_type TEXT DEFAULT 'HYPOTHESIS',
        supporting_evidence_json TEXT DEFAULT '[]',
        contradicting_evidence_json TEXT DEFAULT '[]',
        methodology_comparison TEXT DEFAULT '',
        dataset_comparison TEXT DEFAULT '',
        condition_comparison TEXT DEFAULT '',
        contradiction_strength REAL DEFAULT 0.0,
        possible_explanation TEXT DEFAULT '',
        confidence REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 23. counterfactual_results table — What-if analysis results
    cursor.execute('''CREATE TABLE IF NOT EXISTS counterfactual_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        counterfactual_id TEXT UNIQUE NOT NULL,
        mission_id TEXT,
        hypothesis_id TEXT,
        question TEXT NOT NULL,
        assumptions_json TEXT DEFAULT '[]',
        model_description TEXT DEFAULT '',
        evidence_json TEXT DEFAULT '[]',
        predicted_outcome TEXT DEFAULT '',
        uncertainty REAL DEFAULT 1.0,
        limitations TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 24. knowledge_nodes table — Typed knowledge graph nodes
    cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT UNIQUE NOT NULL,
        node_type TEXT NOT NULL,
        label TEXT NOT NULL,
        properties_json TEXT DEFAULT '{}',
        mission_id TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 25. knowledge_edges table — Typed knowledge graph edges
    cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge_edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_node_id TEXT NOT NULL,
        target_node_id TEXT NOT NULL,
        relation_type TEXT NOT NULL,
        weight REAL DEFAULT 1.0,
        properties_json TEXT DEFAULT '{}',
        mission_id TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 26. user_feedback table
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT,
        hypothesis_title TEXT,
        rating INTEGER,
        feedback_text TEXT,
        user_name TEXT DEFAULT 'Researcher',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 27. team_discussions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS team_discussions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT,
        user_name TEXT NOT NULL,
        comment TEXT NOT NULL,
        tag TEXT DEFAULT 'General',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 28. provenance_records table
    cursor.execute('''CREATE TABLE IF NOT EXISTS provenance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_entity_id TEXT NOT NULL,
        source_entity_type TEXT NOT NULL,
        target_entity_id TEXT NOT NULL,
        target_entity_type TEXT NOT NULL,
        relation TEXT NOT NULL,
        mission_id TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 29. claims_lineage table
    cursor.execute('''CREATE TABLE IF NOT EXISTS claims_lineage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_id TEXT UNIQUE NOT NULL,
        text TEXT NOT NULL,
        claim_type TEXT DEFAULT 'HYPOTHESIS',
        verification_status TEXT DEFAULT 'UNVERIFIED',
        source_ids_json TEXT DEFAULT '[]',
        passage_ids_json TEXT DEFAULT '[]',
        confidence REAL DEFAULT 0.5,
        contradiction_ids_json TEXT DEFAULT '[]',
        mission_id TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 30. death_certificates table
    cursor.execute('''CREATE TABLE IF NOT EXISTS death_certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        certificate_id TEXT UNIQUE NOT NULL,
        hypothesis_id TEXT NOT NULL,
        final_statement TEXT NOT NULL,
        cause_of_failure TEXT NOT NULL,
        fatal_evidence TEXT NOT NULL,
        experiment_responsible TEXT DEFAULT '',
        failed_prediction TEXT DEFAULT '',
        confidence REAL DEFAULT 0.9,
        replication_status TEXT DEFAULT 'FAILED',
        assumptions_violated_json TEXT DEFAULT '[]',
        surviving_components_json TEXT DEFAULT '[]',
        reusable_lessons_json TEXT DEFAULT '[]',
        falsification_stage TEXT DEFAULT 'Adversarial Simulation',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 31. failure_vault table
    cursor.execute('''CREATE TABLE IF NOT EXISTS failure_vault (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        failure_id TEXT UNIQUE NOT NULL,
        hypothesis_id TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        failure_type TEXT NOT NULL,
        parameters_json TEXT DEFAULT '{}',
        environment TEXT DEFAULT 'Sandbox AST v2.0',
        observations TEXT DEFAULT '',
        diagnosis TEXT DEFAULT '',
        confidence REAL DEFAULT 0.9,
        learned_constraint TEXT DEFAULT '',
        future_recommendation TEXT DEFAULT '',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 32. replication_attempts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS replication_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        replication_id TEXT UNIQUE NOT NULL,
        paper_id TEXT NOT NULL,
        experiment_id TEXT NOT NULL,
        reported_result TEXT NOT NULL,
        reproduced_result TEXT NOT NULL,
        absolute_difference REAL DEFAULT 0.0,
        relative_difference REAL DEFAULT 0.0,
        uncertainty REAL DEFAULT 0.05,
        parameter_match REAL DEFAULT 1.0,
        dataset_match REAL DEFAULT 1.0,
        method_match REAL DEFAULT 1.0,
        execution_status TEXT DEFAULT 'SUCCESSFUL',
        replication_status TEXT DEFAULT 'SUCCESSFUL',
        failure_reason TEXT DEFAULT 'NONE',
        multi_run_scores_json TEXT DEFAULT '[]',
        reproducibility_score REAL DEFAULT 90.0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 33. counterfactual_experiments table
    cursor.execute('''CREATE TABLE IF NOT EXISTS counterfactual_experiments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        counterfactual_id TEXT UNIQUE NOT NULL,
        hypothesis_id TEXT NOT NULL,
        varied_dimension TEXT NOT NULL,
        baseline_value TEXT NOT NULL,
        perturbed_value TEXT NOT NULL,
        robustness_score REAL DEFAULT 85.0,
        is_fragile INTEGER DEFAULT 0,
        failure_point_identified TEXT DEFAULT '',
        observations TEXT DEFAULT '',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 34. research_tree_nodes table
    cursor.execute('''CREATE TABLE IF NOT EXISTS research_tree_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT UNIQUE NOT NULL,
        parent_id TEXT,
        node_type TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT DEFAULT 'ACTIVE',
        confidence REAL DEFAULT 0.8,
        mission_id TEXT DEFAULT '',
        data_json TEXT DEFAULT '{}',
        children_ids_json TEXT DEFAULT '[]',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 35. tournament_arguments table
    cursor.execute('''CREATE TABLE IF NOT EXISTS tournament_arguments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        argument_id TEXT UNIQUE NOT NULL,
        tournament_id TEXT NOT NULL,
        round_number INTEGER DEFAULT 1,
        round_name TEXT NOT NULL,
        speaker_role TEXT NOT NULL,
        claim_text TEXT NOT NULL,
        attack_text TEXT NOT NULL,
        defense_text TEXT NOT NULL,
        attack_strength REAL DEFAULT 0.0,
        defense_strength REAL DEFAULT 0.0,
        unresolved_objection TEXT DEFAULT '',
        evidence_refs_json TEXT DEFAULT '[]',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 36. kill_chain_reports table
    cursor.execute('''CREATE TABLE IF NOT EXISTS kill_chain_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hypothesis_id TEXT UNIQUE NOT NULL,
        initial_score REAL DEFAULT 75.0,
        literature_attack_score REAL DEFAULT 70.0,
        contradiction_score REAL DEFAULT 65.0,
        assumption_score REAL DEFAULT 68.0,
        simulation_score REAL DEFAULT 80.0,
        replication_score REAL DEFAULT 78.0,
        statistical_score REAL DEFAULT 82.0,
        final_survival_score REAL DEFAULT 73.0,
        strongest_support TEXT DEFAULT '',
        strongest_contradiction TEXT DEFAULT '',
        critical_assumptions_json TEXT DEFAULT '[]',
        failure_modes_json TEXT DEFAULT '[]',
        recommended_next_action TEXT DEFAULT '',
        disclaimer TEXT DEFAULT 'Empirical resilience score represents survival against simulated falsification; it does not constitute mathematical or physical proof.',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 37. red_team_reports table
    cursor.execute('''CREATE TABLE IF NOT EXISTS red_team_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mission_id TEXT UNIQUE NOT NULL,
        literature_integrity REAL DEFAULT 88.0,
        evidence_integrity REAL DEFAULT 85.0,
        causal_validity REAL DEFAULT 78.0,
        statistical_validity REAL DEFAULT 84.0,
        reproducibility_rating REAL DEFAULT 80.0,
        novelty_rating REAL DEFAULT 86.0,
        overall_research_risk TEXT DEFAULT 'MEDIUM',
        findings_json TEXT DEFAULT '[]',
        cascade_warnings_json TEXT DEFAULT '[]',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 38. active_research_actions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS active_research_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_id TEXT UNIQUE NOT NULL,
        mission_id TEXT NOT NULL,
        action_type TEXT NOT NULL,
        target_hypothesis_id TEXT NOT NULL,
        title TEXT NOT NULL,
        expected_information_gain REAL DEFAULT 0.75,
        estimated_cost_usd REAL,
        estimated_duration_hours REAL,
        risk_level TEXT DEFAULT 'Low',
        feasibility_score REAL DEFAULT 85.0,
        hypothesis_discrimination_power REAL DEFAULT 0.88,
        recommended_rank INTEGER DEFAULT 1,
        reasoning TEXT DEFAULT '',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 39. benchmark_runs table
    cursor.execute('''CREATE TABLE IF NOT EXISTS benchmark_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT UNIQUE NOT NULL,
        task_name TEXT NOT NULL,
        mode TEXT DEFAULT 'BENCHMARK',
        discovery_rate REAL DEFAULT 0.0,
        evidence_accuracy REAL DEFAULT 0.0,
        citation_accuracy REAL DEFAULT 0.0,
        contradiction_recall REAL DEFAULT 0.0,
        latency_seconds REAL DEFAULT 0.0,
        compute_cost_usd REAL DEFAULT 0.0,
        metrics_json TEXT DEFAULT '{}',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 40. telemetry_logs table
    cursor.execute('''CREATE TABLE IF NOT EXISTS telemetry_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mission_id TEXT NOT NULL,
        trace_id TEXT NOT NULL,
        agent_role TEXT NOT NULL,
        model_name TEXT DEFAULT 'fast-router',
        prompt_tokens INTEGER DEFAULT 0,
        completion_tokens INTEGER DEFAULT 0,
        latency_seconds REAL DEFAULT 0.0,
        cost_usd REAL DEFAULT 0.0,
        status TEXT DEFAULT 'SUCCESS',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # --- Evolutionary columns for existing hypotheses table ---
    ensure_column_exists(cursor, "hypotheses", "mission_id", "TEXT")
    ensure_column_exists(cursor, "hypotheses", "generation", "INTEGER DEFAULT 0")
    ensure_column_exists(cursor, "hypotheses", "parent_ids_json", "TEXT DEFAULT '[]'")
    ensure_column_exists(cursor, "hypotheses", "status", "TEXT DEFAULT 'ACTIVE'")

    conn.commit()


