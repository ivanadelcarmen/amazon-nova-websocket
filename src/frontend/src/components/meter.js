import React from 'react';
import './meter.css'
import { Icon, Button, Modal, Box, SpaceBetween, Link, ColumnLayout } from '@cloudscape-design/components';

class Meter extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            // Tokens
            totalInputToken: 0,
            totalOutputToken: 0,
            totalInputSpeechToken: 0,
            totalInputTextToken: 0,
            totalOutputSpeechToken: 0,
            totalOutputTextToken: 0,
            totalToken: 0,

            // Cost
            totalInputSpeechCost: 0,
            totalInputTextCost: 0,
            totalOutputSpeechCost: 0,
            totalOutputTextCost: 0,

            showMeterDetail: false
        };
    }
        
    updateMeter (message) {
        if (message?.event?.usageEvent) {
            const usage = message.event.usageEvent;
            usage.totalToken && this.setState({totalToken: usage.totalToken});
            usage.totalInputTokens && this.setState({totalInputTokens: usage.totalInputTokens});
            usage.totalOutputToken && this.setState({totalOutputToken: usage.totalOutputToken});

            const input = usage.details?.total?.input;
            if (input) {
                input.speechTokens && this.setState({
                    totalInputSpeechToken: input.speechTokens,
                    totalInputSpeechCost: input.speechTokens/1000*0.0034
                });
                input.textTokens && this.setState({
                    totalInputTextToken: input.textTokens,
                    totalInputTextCost: input.textTokens/1000*0.00006
                });
            }

            const output = usage.details?.total?.input;
            if (output) {
                output.speechTokens && this.setState({
                    totalOutputSpeechToken: output.speechTokens,
                    totalOutputSpeechCost: output.speechTokens/1000*0.0136,
                });
                output.textTokens && this.setState({
                    totalOutputTextToken: output.textTokens,
                    totalOutputTextCost: output.textTokens/1000*0.00024
                });
            }
        }
    }

    formatCurrency(value, locale = 'en-US', currency = 'USD') {
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency,
        }).format(value);
    }

    render() {
        return (
            <div className="meter">
                Total cost: {this.formatCurrency(this.state.totalInputTextCost + this.state.totalInputSpeechCost + this.state.totalOutputTextCost + this.state.totalOutputSpeechCost)}
                &nbsp;&nbsp;<Link onClick={()=>{this.setState({showMeterDetail: true})}}><Icon name="support" /></Link>
                <Modal
                    onDismiss={() => this.setState({showMeterDetail: false})}
                    visible={this.state.showMeterDetail}
                    header="Total tokens and cost"
                    size='large'
                    footer={
                        <Box float="right">
                        <SpaceBetween direction="horizontal" size="xs">
                            <Button variant="link" onClick={() => this.setState({showMeterDetail: false})}>Close</Button>
                        </SpaceBetween>
                        </Box>
                    }
                >
                    <div className='meterdetail'>
                        <ColumnLayout columns={2} borders="horizontal">
                            <div>
                                Total tokens: {this.state.totalToken.toLocaleString()} <br/>
                                Total cost: {this.formatCurrency(this.state.totalInputTextCost + this.state.totalInputSpeechCost + this.state.totalOutputTextCost + this.state.totalOutputSpeechCost)}<br/>
                            </div>
                            <div>
                                Total input tokens: {this.state.totalInputToken.toLocaleString()} <br/>
                                Total output tokens: {this.state.totalOutputToken.toLocaleString()} <br/>
                            </div>
                            <div>
                                Total input speech tokens: {this.state.totalInputSpeechToken.toLocaleString()}
                            </div>
                            <div>
                                Total input text tokens: {this.state.totalInputTextToken.toLocaleString()}
                            </div>
                            <div>
                                Total output speech tokens: {this.state.totalOutputSpeechToken.toLocaleString()}
                            </div>
                            <div>
                                Total output text tokens: {this.state.totalOutputTextToken.toLocaleString()}
                            </div>
                        </ColumnLayout>
                    </div>
                </Modal>
                
            </div>
        );
    }
}

export default Meter;