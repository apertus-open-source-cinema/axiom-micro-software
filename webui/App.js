import React,  { Component } from 'react';
import './index.css';
import flatten from 'flat'
import NumericInputSlider from './NumericInputSlider'

const base_url = "http://axiom-micro:5000/";

export default class App extends Component {
    constructor() {
        super();

        this.state = {
            values: {},
        };
        
        fetch(base_url).then((result) => {
            result.json().then(json => {
                this.setState({values: flatten(json, {delimiter: "/"})});
            })
        });
    }

    render() {
        return (
            <div style={{
                textAlign: "center",
                height: "100%",
                width: "100%",

                backgroundColor: "#333",
                color: "#fff",
            }}>
            {Object.keys(this.state.values).reverse().map((key, i) => {
                const value = this.state.values[key];
                return (
                    <NumericInputSlider 
                        value={value}
                        onChange={value => {
                            fetch(base_url + key, {method: "PUT", body: value}).then(r => r.json().then(v => {
                                console.log(v)
                                this.setState({values: Object.assign(this.state.values, {[key]: v})})
                            }));
                        }}
                        name={key}
                        theme={i % 2 == 0}
                        key={i}
                    />
                )
            })}
            <div 
                onClick={() => {
                    if (!document.webkitFullscreenElement) {
                        document.documentElement.webkitRequestFullscreen();
                    } else {
                        document.webkitExitFullscreen(); 
                    }
                }}
                style={{padding: "10px"}}
            >
                    Fullscreen
            </div>
            </div>
        );
    }
}
