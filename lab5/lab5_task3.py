import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go

# --- Параметри ---
t = np.linspace(0, 2 * np.pi, 1000)
init = {
    'A': 1.0,
    'f': 1.0,
    'phi': 0.0,
    'noise_mean': 0.0,
    'noise_std': 0.3,
    'filter_window': 10,
}

# --- Чиста гармоніка ---
def pure_harmonic(A, f, phi):
    return A * np.sin(2 * np.pi * f * t + phi)

# --- Генерація шуму ---
def generate_noise(mean, std, size=1000, seed=None):
    if seed is not None:
        np.random.seed(seed)
    return np.random.normal(mean, std, size)

# --- Фільтр (ковзне середнє) ---
def moving_average_filter(signal, window_size):
    filtered = np.convolve(signal, np.ones(window_size)/window_size, mode='same')
    return filtered

# --- Початкові дані ---
noise = generate_noise(init['noise_mean'], init['noise_std'])
pure = pure_harmonic(init['A'], init['f'], init['phi'])
noisy = pure + noise
filtered = moving_average_filter(noisy, init['filter_window'])

# --- Dash App ---
app = Dash(__name__)
app.layout = html.Div([
    html.H2("Гармоніка з шумом та фільтрація (Plotly + власний фільтр)"),
    dcc.Graph(id='harmonic-plot'),

    html.Div([
        html.Label("Амплітуда (A)"),
        dcc.Slider(0.1, 5.0, step=0.1, value=init['A'], id='amp-slider'),
        html.Label("Частота (f)"),
        dcc.Slider(0.1, 5.0, step=0.1, value=init['f'], id='freq-slider'),
        html.Label("Фаза (phi)"),
        dcc.Slider(0, 2*np.pi, step=0.1, value=init['phi'], id='phi-slider'),
        html.Label("Середнє шуму"),
        dcc.Slider(-1, 1, step=0.1, value=init['noise_mean'], id='mean-slider'),
        html.Label("Стд. відх. шуму"),
        dcc.Slider(0.01, 1.0, step=0.01, value=init['noise_std'], id='std-slider'),
        html.Label("Вікно фільтру (розмір)"),
        dcc.Slider(1, 100, step=1, value=init['filter_window'], id='filter-slider'),
    ], style={'width': '45%', 'display': 'inline-block', 'padding': '20px'}),

    html.Div([
        html.Label("Що показувати:"),
        dcc.Checklist(
            ['Чиста', 'З шумом', 'Фільтрована'],
            ['Чиста', 'З шумом', 'Фільтрована'],
            id='show-options'
        ),
        html.Label("Вибір кольору фільтрованої"),
        dcc.Dropdown(
            ['green', 'red', 'blue', 'orange'],
            value='green',
            id='filter-color'
        ),
    ], style={'width': '45%', 'display': 'inline-block', 'padding': '20px'}),
])

@app.callback(
    Output('harmonic-plot', 'figure'),
    Input('amp-slider', 'value'),
    Input('freq-slider', 'value'),
    Input('phi-slider', 'value'),
    Input('mean-slider', 'value'),
    Input('std-slider', 'value'),
    Input('filter-slider', 'value'),
    Input('show-options', 'value'),
    Input('filter-color', 'value')
)
def update_plot(A, f, phi, noise_mean, noise_std, filt_window, show_opts, filt_color):
    pure = pure_harmonic(A, f, phi)
    noise = generate_noise(noise_mean, noise_std, size=len(t))
    noisy = pure + noise
    filtered = moving_average_filter(noisy, int(filt_window))

    fig = go.Figure()
    if 'Чиста' in show_opts:
        fig.add_trace(go.Scatter(x=t, y=pure, mode='lines', name='Чиста гармоніка'))
    if 'З шумом' in show_opts:
        fig.add_trace(go.Scatter(x=t, y=noisy, mode='lines', name='З шумом'))
    if 'Фільтрована' in show_opts:
        fig.add_trace(go.Scatter(x=t, y=filtered, mode='lines', name='Фільтрована', line=dict(color=filt_color)))

    fig.update_layout(title='Інтерактивна візуалізація гармоніки',
                      xaxis_title='Час',
                      yaxis_title='Амплітуда',
                      height=600)
    return fig

if __name__ == '__main__':
    app.run(debug=True)
