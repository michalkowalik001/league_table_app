import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Custom League Table Calculator")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV file", type="csv")

# Calculation mode
calc_mode = st.radio("Calculation Mode", ["Standard Win/Draw/Loss", "Based on Goal Difference"])

# Input parameters
if calc_mode == "Standard Win/Draw/Loss":
    win_points = st.number_input("Points for Win", value=3)
    tie_points = st.number_input("Points for Tie", value=1)
    loss_points = st.number_input("Points for Loss", value=0)
else:
    st.subheader("Points by Goal Difference")
    gd1_win = st.number_input("Win by 1 goal", value=2)
    gd1_loss = st.number_input("Loss by 1 goal", value=-1)
    gd2_win = st.number_input("Win by 2 goals", value=3)
    gd2_loss = st.number_input("Loss by 2 goals", value=-2)
    gd3_win = st.number_input("Win by 3+ goals", value=4)
    gd3_loss = st.number_input("Loss by 3+ goals", value=-3)

    st.subheader("Points for Draws")
    draw_0 = st.number_input("0-0 Draw", value=1)
    draw_1 = st.number_input("1-1 Draw", value=2)
    draw_2 = st.number_input("2-2 Draw", value=2)
    draw_3 = st.number_input("3-3+ Draw", value=3)

def calculate_standard(df, win_points, tie_points, loss_points):
    teams = pd.unique(df[['HomeTeam', 'AwayTeam']].values.ravel())
    standings = pd.DataFrame({
        "Team": teams,
        "Wins": 0,
        "Ties": 0,
        "Losses": 0,
        "Points_mod": 0,
        "Points_standard": 0,
        "Goals_Scored": 0,
        "Goals_Conceded": 0
    }).set_index("Team")

    for _, row in df.iterrows():
        home, away = row['HomeTeam'], row['AwayTeam']
        hg, ag = row['HomeGoals'], row['AwayGoals']

        standings.loc[home, "Goals_Scored"] += hg
        standings.loc[home, "Goals_Conceded"] += ag
        standings.loc[away, "Goals_Scored"] += ag
        standings.loc[away, "Goals_Conceded"] += hg

        if hg > ag:
            standings.loc[home, ["Wins", "Points_mod", "Points_standard"]] += [1, win_points, 3]
            standings.loc[away, ["Losses", "Points_mod"]] += [1, loss_points]
        elif hg < ag:
            standings.loc[away, ["Wins", "Points_mod", "Points_standard"]] += [1, win_points, 3]
            standings.loc[home, ["Losses", "Points_mod"]] += [1, loss_points]
        else:
            standings.loc[[home, away], ["Ties", "Points_mod", "Points_standard"]] += [1, tie_points, 1]

    standings["Goal_Difference"] = standings["Goals_Scored"] - standings["Goals_Conceded"]
    standings = standings.sort_values(["Points_mod", "Goal_Difference", "Goals_Scored"], ascending=False)
    standings["Rank"] = range(1, len(standings) + 1)
    return standings.reset_index()

def calculate_goal_diff(df):
    teams = pd.unique(df[['HomeTeam', 'AwayTeam']].values.ravel())
    standings = pd.DataFrame({
        "Team": teams,
        "Wins": 0,
        "Ties": 0,
        "Losses": 0,
        "Points_mod": 0,
        "Points_standard": 0,
        "Goals_Scored": 0,
        "Goals_Conceded": 0
    }).set_index("Team")

    for _, row in df.iterrows():
        home, away = row['HomeTeam'], row['AwayTeam']
        hg, ag = row['HomeGoals'], row['AwayGoals']

        standings.loc[home, "Goals_Scored"] += hg
        standings.loc[home, "Goals_Conceded"] += ag
        standings.loc[away, "Goals_Scored"] += ag
        standings.loc[away, "Goals_Conceded"] += hg

        # Standard points
        if hg > ag:
            standings.loc[home, ["Wins", "Points_standard"]] += [1, 3]
            standings.loc[away, "Losses"] += 1
        elif hg < ag:
            standings.loc[away, ["Wins", "Points_standard"]] += [1, 3]
            standings.loc[home, "Losses"] += 1
        else:
            standings.loc[[home, away], ["Ties", "Points_standard"]] += [1, 1]

        # Modified points
        if hg == ag:
            draw_goals = min(hg, 3)
            draw_points = {0: draw_0, 1: draw_1, 2: draw_2, 3: draw_3}[draw_goals]
            standings.loc[[home, away], "Points_mod"] += draw_points
        else:
            diff = abs(hg - ag)
            if diff == 1:
                win_val, lose_val = gd1_win, gd1_loss
            elif diff == 2:
                win_val, lose_val = gd2_win, gd2_loss
            else:
                win_val, lose_val = gd3_win, gd3_loss

            if hg > ag:
                standings.loc[home, "Points_mod"] += win_val
                standings.loc[away, "Points_mod"] += lose_val
            else:
                standings.loc[away, "Points_mod"] += win_val
                standings.loc[home, "Points_mod"] += lose_val

    standings["Goal_Difference"] = standings["Goals_Scored"] - standings["Goals_Conceded"]
    standings = standings.sort_values(["Points_mod", "Goal_Difference", "Goals_Scored"], ascending=False)
    standings["Rank"] = range(1, len(standings) + 1)
    return standings.reset_index()

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    try:
        if calc_mode == "Standard Win/Draw/Loss":
            standings = calculate_standard(df, win_points, tie_points, loss_points)
        else:
            standings = calculate_goal_diff(df)

        st.subheader("Standings Table")
        st.dataframe(standings)

        st.subheader("Points Comparison Plot")
        fig, ax = plt.subplots()
        ax.scatter(standings["Points_mod"], standings["Team"], color="blue", label="Modified Points", s=100)
        ax.scatter(standings["Points_standard"], standings["Team"], color="red", label="Standard Points", s=100)
        ax.set_xlabel("Points")
        ax.set_ylabel("Team")
        ax.set_title("Standard vs Modified Points")
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")
