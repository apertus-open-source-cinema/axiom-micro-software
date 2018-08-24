import React,  { Component } from 'react';

export default class NumericInputSlider extends Component {
    constructor() {
        super();

        this.state = {
            down: false,
            startPos: [NaN, NaN],
            startVal: 0,
            value: 0,
            type: parseFloat,
        };
    }

    componentDidMount() {
        const type = this.props.value.includes(".") ? parseFloat : parseInt;
        this.setState({value: type(this.props.value), type: type});
    }

    render() {
        const move = (e) => {
            if(this.state.down) {
                let base = e;
                if(e.touches) {
                    base = e.touches[0]
                }

                const x = base.clientX;
                const y = base.clientY;
                if(isNaN(this.state.startPos[0]) && isNaN(this.state.startPos[0])) {
                    this.setState({startPos: [x, y]})
                } else {
                    const [dx, dy] = [x - this.state.startPos[0], y - this.state.startPos[1]]
                    const newVal = this.state.startVal + dx / 100;
                    this.setState({value: newVal})
                }
            }
        }
        const join = () => {this.setState({down: true, startVal: this.state.type(this.props.value)})};
        const leafe = () => {this.setState({down: false, startPos: [NaN, NaN]}); this.props.onChange(this.state.type(this.state.value))};

        if(!this.state.down) {
            setTimeout(() => this.setState({value: this.state.type(this.props.value)}), 0)
        }
       
        return (
            <div
                style={{padding: "30px", backgroundColor: this.props.theme ? '#111' : '#222'}}
                onMouseDown={join}
                onTouchStartCapture={join}
    
                onMouseUp={leafe}
                onTouchEnd={leafe}
    
                onMouseMove={move}
                onTouchMove={move}
            >
                <span style={{display: 'block', opacity: 0.5, userSelect: "none"}}>{this.props.name}</span>
                <span
                    style={{
                        fontSize: "50px",
                        width: "50%",
                        textAlign: "center",
                        border: "none",
                        outline: "none",
                        backgroundColor: "inherit",
                        color: "inherit",
                        userSelect: "none",
                    }}
                >
                    {this.state.type == parseInt ? parseInt(this.state.value) : this.state.value.toFixed(2)}
                </span>
            </div>
        );
    }
}
