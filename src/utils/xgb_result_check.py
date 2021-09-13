import google.auth

from .helper import read_bigquery, write


class ResultCheck:
    def __init__(self):
        self.results = read_bigquery('df_all_sorted').iloc[::-1].reset_index(drop=True)
        self.predicted_results = read_bigquery('xgb_next_games_pred').sort_values('home_team_name').reset_index(
            drop=True)
        self.credentials, self.project_id = google.auth.default()

    def actual_results(self):
        df = self.results
        df_last_completed = df[df['status'] == 'complete'].head(9).sort_values('home_team_name')
        df_last_completed['goal_diff'] = df_last_completed['home_team_goal_count'] - df_last_completed[
            'away_team_goal_count']

        for index, row in df_last_completed[df_last_completed['status'] == 'complete'].iterrows():
            if df_last_completed['goal_diff'][index] > 0:
                df_last_completed.at[index, 'real_result'] = 3
            elif df_last_completed['goal_diff'][index] == 0:
                df_last_completed.at[index, 'real_result'] = 2
            else:
                df_last_completed.at[index, 'real_result'] = 1
        return df_last_completed.reset_index(drop=True)

    def possible_win(self):
        df = self.actual_results()

        for index, row in df.iterrows():
            if df['real_result'][index] == self.predicted_results['predicted_result'][index]:
                if df['real_result'][index] == 3:
                    df.at[index, 'possible_win'] = df['odds_ft_home_team_win'][index] * 10
                elif df['real_result'][index] == 0:
                    df.at[index, 'possible_win'] = df['odds_ft_draw'][index] * 10
                else:
                    df.at[index, 'possible_win'] = df['odds_ft_away_team_win'][index] * 10

        df['predicted_results'] = self.predicted_results['predicted_result']
        write(df, self.project_id, 'statistics', 'xgb_result_check', self.credentials)
        return df
